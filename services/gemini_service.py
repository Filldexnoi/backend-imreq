import re
import base64
import io
import logging
from typing import Dict, List, Optional
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from services.llm_provider import get_llm_provider, LLMProvider
from services.similarity_utils import compute_semantic_similarity as _sem_sim

logger = logging.getLogger(__name__)

class GeminiService:
    """
    Optimized Gemini Service with parallel processing
    """
    TEMPLATE_DEFINITIONS: Dict[str, Dict[str, str]] = {
        "EARS": {
            "name": "EARS (Easy Approach to Requirements Syntax)",
            "description": "EARS provides 5 syntax patterns for writing requirements",
            "patterns": """
1. Ubiquitous (Always active): "The [system] shall [requirement]"
2. State-driven: "WHILE [in a state], the [system] shall [requirement]"
3. Event-driven: "WHEN [trigger], the [system] shall [requirement]"
4. Unwanted behavior: "IF [unwanted condition], THEN the [system] shall [requirement]"
5. Optional feature: "WHERE [feature included], the [system] shall [requirement]"

Key characteristics:
- Uses "shall" for mandatory requirements
- Clear trigger conditions (WHEN, WHILE, IF, WHERE)
- Single responsibility per requirement
- Avoids ambiguous words (may, might, can, should in conditions)
"""
        },
        "ISO29148": {
            "name": "ISO/IEC/IEEE 29148",
            "description": "ISO 29148 standard for requirement writing",
            "patterns": """
General guidelines:
- Use "shall" for mandatory requirements
- Use "should" for recommended features (use sparingly)
- Avoid ambiguous terms (may, might, can, probably, as appropriate)
- Each requirement should be atomic (singular)
- Use clear, concise language
- Include measurable criteria when possible
- Use active voice

Example patterns:
- "The [system] shall [action] [object] [criteria]"
- "The [function] shall provide [capability]"
- Avoid: "The system should be user-friendly" (ambiguous)
- Better: "The system shall respond to user actions within 2 seconds"
"""
        },
        "Others": {
            "name": "Custom/No specific template",
            "description": "No specific template applied",
            "patterns": "Requirements may follow custom organizational standards or no specific template."
        }
    }
    
    def __init__(self, max_workers: int = 10, llm_provider: Optional[LLMProvider] = None):
        self.llm: LLMProvider = llm_provider if llm_provider is not None else get_llm_provider()
        self.max_workers = max_workers

    @staticmethod
    def _detect_language(text: str) -> str:
        """Return 'Thai' if text contains Thai characters, otherwise 'English'."""
        if re.search(r'[\u0e00-\u0e7f]', text):
            return "Thai"
        return "English"

    def _extract_reference_text(self, reference_files: list) -> Optional[str]:
        """
        Decode base64 reference files and extract plain text.
        Supports PDF (pdfplumber), TXT/Markdown, and DOCX (python-docx).
        Returns None if no files or all extractions fail.
        Truncates combined output to ~10 000 chars to stay within token budget.
        """
        if not reference_files:
            return None

        texts = []
        for file_info in reference_files:
            name = file_info.get("name", "")
            content_b64 = file_info.get("content", "")
            file_type = file_info.get("type", "")

            try:
                content_bytes = base64.b64decode(content_b64)

                if file_type == "application/pdf" or name.lower().endswith(".pdf"):
                    import pdfplumber
                    with pdfplumber.open(io.BytesIO(content_bytes)) as pdf:
                        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                    text = text.strip()
                    if not text:
                        logger.warning(f"[ref_extract] '{name}': PDF extracted empty text (scanned/image PDF?)")
                    else:
                        logger.info(f"[ref_extract] '{name}': extracted {len(text)} chars from PDF")
                    texts.append(f"[{name}]\n{text}")

                elif file_type in ("text/plain", "text/markdown") or name.lower().endswith((".txt", ".md")):
                    text = content_bytes.decode("utf-8", errors="ignore").strip()
                    logger.info(f"[ref_extract] '{name}': extracted {len(text)} chars from text")
                    texts.append(f"[{name}]\n{text}")

                elif "word" in file_type or name.lower().endswith(".docx"):
                    import docx
                    doc = docx.Document(io.BytesIO(content_bytes))
                    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
                    logger.info(f"[ref_extract] '{name}': extracted {len(text)} chars from DOCX")
                    texts.append(f"[{name}]\n{text}")

                else:
                    logger.warning(f"[ref_extract] '{name}': unsupported type '{file_type}' — skipped")

            except Exception as e:
                logger.error(f"[ref_extract] '{name}': extraction failed — {type(e).__name__}: {e}")
                continue

        if not texts:
            logger.warning("[ref_extract] No text extracted from any reference file")
            return None

        combined = "\n\n---\n\n".join(texts)
        if len(combined) > 10000:
            combined = combined[:10000] + "\n...[truncated]"
        return combined

    CRITERIA_NAMES = [
        "Appropriate", "Complete", "Conforming", "Correct",
        "Feasible", "Necessary", "Singular", "Unambiguous", "Verifiable",
    ]

    # ISO 29148 writing rules (from sections 5.2.4 and 5.2.7)
    RULES: List[Dict] = [
        {"section": "5.2.4", "name": "Modal Verb 'Should'",       "description": "Use 'should' to denote a non-mandatory goal, preference, or recommended practice."},
        {"section": "5.2.4", "name": "Active Voice",               "description": "Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is required that...')."},
        {"section": "5.2.7", "name": "Subjective Language",        "description": "Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative criteria."},
        {"section": "5.2.7", "name": "Open-ended Terms",           "description": "Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope."},
        {"section": "5.2.4", "name": "System Performance",         "description": "Requirements should define the performance of the system, not a capability of the user or operator."},
        {"section": "5.2.7", "name": "Vague Pronouns",             "description": "Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for clarity."},
        {"section": "5.2.4", "name": "Avoid 'Must'",               "description": "Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding requirements."},
        {"section": "5.2.4", "name": "Positive Phrasing",          "description": "Requirements should be stated as positive statements (what the system shall do) rather than negative (shall not)."},
        {"section": "5.2.4", "name": "Measurable Conditions",      "description": "A well-formed requirement is qualified by measurable conditions that define its boundaries."},
        {"section": "5.2.7", "name": "Superlatives",               "description": "Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable constraints."},
        {"section": "5.2.7", "name": "Comparative Phrases",        "description": "Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined baseline."},
        {"section": "5.2.7", "name": "Loopholes",                  "description": "Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not limited to'."},
        {"section": "5.2.4", "name": "Avoid 'Shall be able to'",   "description": "Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The system shall [Action]')."},
        {"section": "5.2.4", "name": "Formal Syntax",              "description": "A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object] [Constraint]."},
        {"section": "5.2.4", "name": "Modal Verb 'Shall'",         "description": "Use 'shall' to denote a binding, mandatory requirement that is contractually required."},
        {"section": "5.2.7", "name": "Design Independence",        "description": "Requirements should state 'what' is needed, not 'how'. Do not include design decisions or commercial products."},
        {"section": "5.2.7", "name": "Ambiguous Adjectives",       "description": "Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'."},
    ]

    # Which rules are relevant per criterion (for focused prompt injection)
    RULES_BY_CRITERION: Dict[str, List[str]] = {
        "Appropriate":  ["Design Independence", "System Performance"],
        "Complete":     ["Formal Syntax", "Open-ended Terms"],
        "Conforming":   ["Modal Verb 'Shall'", "Modal Verb 'Should'", "Avoid 'Must'",
                         "Active Voice", "Positive Phrasing", "Formal Syntax", "Avoid 'Shall be able to'"],
        "Correct":      [],
        "Feasible":     [],
        "Necessary":    [],
        "Singular":     ["Open-ended Terms"],
        "Unambiguous":  ["Subjective Language", "Vague Pronouns", "Ambiguous Adjectives",
                         "Superlatives", "Comparative Phrases", "Loopholes"],
        "Verifiable":   ["Measurable Conditions", "Open-ended Terms", "Superlatives"],
    }

    def _build_rules_reference(self, criterion: str) -> str:
        """Build a rules reference string for the given criterion (for LLM prompt)."""
        rule_names = self.RULES_BY_CRITERION.get(criterion, [])
        if not rule_names:
            return ""
        rules_lookup = {r["name"]: r for r in self.RULES}
        lines = []
        for name in rule_names:
            r = rules_lookup.get(name)
            if r:
                lines.append(f'- "{name}" (§{r["section"]}): {r["description"]}')
        if not lines:
            return ""
        return "\nReference rules (cite relevant ones in cited_rules):\n" + "\n".join(lines)

    # Per-criterion evaluation instructions (focused, single-responsibility)
    CRITERION_INSTRUCTIONS: Dict[str, str] = {
        "Appropriate": """The requirement must state WHAT the system shall do, not HOW.
It must NOT impose unnecessary design or architectural constraints.

Checks to perform:
1. Design Constraint Check: Scan for commercial product names, vendor names, specific technology brands, or explicit architecture/implementation choices (e.g., "use React", "store in MySQL", "deploy on AWS"). If found at system-requirement level → FAIL; name the exact term.
2. Tolerance/Detail Level Check: If numeric tolerances or component-level specifications appear in what should be a high-level system requirement → FAIL; identify the over-specified detail.""",

        "Complete": """The requirement must be self-contained and understandable without consulting external sources.

Checks to perform:
1. Self-Contained Check: Verify the sentence has a clear subject (WHO/WHAT system), action (SHALL do), and condition or measurable outcome. FAIL if any slot is missing; name the missing slot.
2. Reference Check: If the requirement cites another document without specifying a version number or date → FAIL; name the unversioned reference.""",

        "Conforming": """The requirement must follow the approved template and standard writing conventions.

Template in use: {template_name}
Template patterns:
{template_patterns}

Checks to perform:
1. Mandatory Keyword Check: FAIL if obligation is expressed using "will", "should", or "may" instead of "shall" (or "ต้อง" in Thai) for mandatory requirements.
2. Voice Check: FAIL if the requirement uses passive voice (e.g., "shall be processed by", "will be handled"). Active voice required.
3. Negative Constraint Check: FAIL if the requirement uses "shall not" form; recommend rewriting as a positive statement.
4. Template Pattern Check: Identify which template pattern this requirement matches (or "None" if it does not match any).

Return these extra fields in your JSON:
- "detected_pattern": e.g. "EARS: Event-driven", "ISO29148: Standard", "None" """,

        "Correct": """The requirement must accurately represent the original stakeholder need it was derived from.

{ref_block}

Check to perform:
- IF reference documents are provided:
  Search the reference for any section describing the intent, scope, or source of this type of requirement.
  Use BROAD matching — look for any passage that could be the basis or motivation for this requirement.
  PASS if the requirement's intent is consistent with any described need in the reference; quote the relevant passage.
  FAIL if the requirement contradicts or significantly misrepresents the described intent; quote both.
  CANNOT_DETERMINE only if the reference contains no information at all relevant to this requirement.
- OTHERWISE → CANNOT_DETERMINE.""",

        "Feasible": """The requirement must be achievable within real-world constraints (cost, schedule, technical readiness).

{ref_block}

Check to perform:
- IF reference documents are provided:
  Read ALL sections looking for: technology stack, platform requirements, database type, operational limits, regulatory requirements, team/methodology constraints.
  PASS (default) if the requirement does not conflict with any stated constraint; quote the most relevant constraint.
  FAIL only if the requirement directly conflicts with a specific stated constraint; quote both the conflicting constraint and the problematic requirement text.
  Do NOT return CANNOT_DETERMINE when constraints are present — use them to make a determination.
- OTHERWISE → CANNOT_DETERMINE.""",

        "Necessary": """A requirement is necessary only if it can be traced back to a stakeholder need, business goal, or objective, AND it has not become obsolete.

{ref_block}

Checks to perform:
1. Traceability Check:
   IF reference documents are provided:
     Use BROAD matching — semantic alignment is sufficient (e.g., "user account management" matches "Managing user and group accounts and privileges").
     PASS if the requirement addresses any need, goal, or capability described anywhere in the reference; quote the most relevant sentence.
     FAIL if the requirement is completely outside the scope of the reference (potential gold-plating); explain.
     Do NOT return CANNOT_DETERMINE just because there is no exact wording match.
   OTHERWISE → CANNOT_DETERMINE.
2. Expiration Check (always apply regardless of reference):
   FAIL if the requirement contains time-bound language that may already be obsolete (e.g., past deadlines, discontinued systems, outdated standards).""",

        "Singular": """One requirement must express exactly one capability, characteristic, constraint, or quality factor.

Check to perform:
- Conjunction Check: Scan for "and", "or", "and/or" (and their Thai equivalents: และ, หรือ, และ/หรือ).
  If found linking two distinct capabilities or actions → FAIL; list each distinct capability that should be split into a separate requirement.
  NOTE: conjunctions inside a single condition (e.g., "username and password") are acceptable — only FAIL when two independent capabilities are joined.""",

        "Unambiguous": """The requirement must have exactly one valid interpretation.

Check to perform:
- Vague Words Check: Scan for the following categories and list every offending term:
  • Superlatives: best, most, fastest, highest, lowest, optimal
  • Subjective quality: user-friendly, easy to use, intuitive, cost-effective, simple, robust, flexible
  • Vague adverbs/adjectives: almost always, significant, minimal, sufficient, appropriate, adequate, reasonable
  • Loophole phrases: if possible, as appropriate, as applicable, where necessary, etc.
FAIL if any such term is found; name each term and explain why it creates ambiguity.""",

        "Verifiable": """The requirement must be written so that compliance can be tested or measured objectively.

Checks to perform:
1. Measurable Condition Check: FAIL if the requirement lacks numbers, units, thresholds, or observable conditions needed to write a test case.
2. Open-ended Word Check: Scan for the following and FAIL if found; name each term:
   • "provide support", "but not limited to", "as a minimum", "etc."
   • Absolute universals that are untestable: "all", "every", "always", "never"
   Explain why each term prevents objective verification.""",
    }

    def _analyze_single_criterion(
        self,
        criterion: str,
        requirement: str,
        req_id: str,
        requirement_template: str = "Others",
        reference_context: str = None,
    ) -> Dict:
        """Evaluate ONE ISO 29148 criterion for ONE requirement."""
        # Build criterion-specific instruction (substitute placeholders)
        instruction = self.CRITERION_INSTRUCTIONS[criterion]

        ref_block = f"""Reference documents provided (use as ground truth):
---
{reference_context}
---""" if reference_context else "No reference documents provided."

        if criterion == "Conforming":
            template_info = self.TEMPLATE_DEFINITIONS.get(requirement_template, self.TEMPLATE_DEFINITIONS["Others"])
            instruction = instruction.format(
                template_name=requirement_template,
                template_patterns=template_info["patterns"],
            )
        elif "{ref_block}" in instruction:
            instruction = instruction.format(ref_block=ref_block)

        rules_reference = self._build_rules_reference(criterion)
        extra_fields = '\n  "detected_pattern": "<pattern or null>",' if criterion == "Conforming" else ""

        req_lang = self._detect_language(requirement)
        prompt = f"""You are an ISO/IEC/IEEE 29148 requirements quality expert.
Evaluate the requirement below against the "{criterion}" criterion ONLY.
Do NOT evaluate any other criterion.
Do NOT assume missing information — mark CANNOT_DETERMINE when required context is absent.

OUTPUT LANGUAGE: {req_lang}. The "reason" field MUST be written in {req_lang} only. Do not use any other language.

Requirement: "{requirement}" (ID: {req_id})

--- Criterion: {criterion} ---
{instruction}
{rules_reference}

Return JSON only:
{{
  "criterion": "{criterion}",{extra_fields}
  "status": "PASS" | "FAIL" | "CANNOT_DETERMINE",
  "reason": "<FAIL: what is wrong | PASS: why it passes | CANNOT_DETERMINE: what context is missing>",
  "cited_rules": ["<rule name>"]
}}
cited_rules must be a list of rule names from the reference above that apply to the finding (empty list [] if none apply or no rules reference was given)."""

        try:
            result_text = self.llm.generate_json(prompt)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            data = json.loads(result_text)
            return {
                "criterion": criterion,
                "status": data.get("status", "FAIL"),
                "reason": data.get("reason", ""),
                "cited_rules": data.get("cited_rules") or [],
                "detected_pattern": data.get("detected_pattern"),
            }
        except Exception as e:
            return {
                "criterion": criterion,
                "status": "FAIL",
                "reason": f"เกิดข้อผิดพลาดในการประเมิน: {e}",
                "cited_rules": [],
                "detected_pattern": None,
            }

    def _analyze_single_requirement_all_criteria(
        self,
        requirement: str,
        req_id: str,
        requirement_template: str = "Others",
        reference_context: str = None,
        enabled_criteria: list = None,
    ) -> Dict:
        """
        Analyze ONE requirement against selected ISO 29148 criteria.
        Each criterion is evaluated by a separate focused LLM call, all run in parallel.
        If enabled_criteria is None or empty, all 9 criteria are used.
        """
        active_criteria = (
            [c for c in self.CRITERIA_NAMES if c in enabled_criteria]
            if enabled_criteria else self.CRITERIA_NAMES
        )

        criterion_results: Dict[str, Dict] = {}

        with ThreadPoolExecutor(max_workers=len(active_criteria)) as executor:
            futures = {
                executor.submit(
                    self._analyze_single_criterion,
                    criterion, requirement, req_id, requirement_template, reference_context,
                ): criterion
                for criterion in active_criteria
            }
            for future in as_completed(futures):
                result = future.result()
                criterion_results[result["criterion"]] = result

        # Rebuild in canonical order (only active criteria)
        results_list = [criterion_results[c] for c in active_criteria if c in criterion_results]

        passed_criteria = []
        failed_evaluation = {}
        total_score = 0

        for r in results_list:
            criterion = r["criterion"]
            status = r["status"]
            reason = r.get("reason", "") or ""
            cited_rules = r.get("cited_rules") or []

            if status == "PASS":
                passed_criteria.append(criterion)
                total_score += 1
            else:
                if status == "CANNOT_DETERMINE":
                    reason = f"[?] {reason}" if reason else "[?] ไม่สามารถประเมินได้เนื่องจากขาด context"
                elif criterion == "Conforming":
                    reason = f"[Template: {requirement_template}] {reason}"
                failed_evaluation[criterion] = {
                    "reason": reason or "ไม่ผ่านเกณฑ์",
                    "cited_rules": cited_rules,
                }

        total_criteria = len(active_criteria)
        return {
            "req_id": req_id,
            "score": f"{total_score}/{total_criteria}",
            "characteristics": passed_criteria,
            "evaluation": failed_evaluation,
            "detailed_results": results_list,
        }
    
    async def analyze_requirements_parallel(
        self,
        requirements: List[Dict],
        requirement_template: str = "Others",
        progress_callback=None,
        reference_context: str = None,
        enabled_criteria: list = None,
    ) -> Dict:
        """
        Analyze requirements in parallel.
        reference_context: extracted text from project reference files,
        used as ground truth for Necessary, Feasible, and Correct criteria.
        enabled_criteria: list of criterion names to evaluate; None = all 9.
        """
        total = len(requirements)
        results = []

        # Create async tasks
        loop = asyncio.get_event_loop()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                loop.run_in_executor(
                    executor,
                    self._analyze_single_requirement_all_criteria,
                    req['requirement'],
                    req['req_id'],
                    requirement_template,
                    reference_context,
                    enabled_criteria,
                )
                for req in requirements
            ]
            
            # Process as they complete
            completed = 0
            for future in asyncio.as_completed(futures):
                result = await future
                results.append(result)
                completed += 1
                
                # Progress callback
                if progress_callback:
                    await progress_callback(completed, total)
        
        # Calculate summary
        total_score_sum = sum(
            int(r['score'].split('/')[0]) 
            for r in results 
            if r.get('score')
        )
        avg_score = total_score_sum / total if total > 0 else 0
        
        return {
            "results": results,
            "summary": {
                "total_analyzed": total,
                "average_score": f"{avg_score:.1f}/9",
                "recommendations": self._generate_recommendations(results),
                "analysis_method": "parallel_detailed"
            }
        }
    
    def analyze_requirements_parallel_sync(
        self,
        requirements: List[Dict],
        requirement_template: str = "Others",
        entity_level: str = None,
        business_goals: str = None,
        constraints: str = None,
    ) -> Dict:
        """
        Synchronous version for non-async contexts
        """
        return asyncio.run(self.analyze_requirements_parallel(
            requirements, requirement_template,
            entity_level=entity_level,
            business_goals=business_goals,
            constraints=constraints,
        ))
    
    def _generate_recommendations(self, results: List[Dict]) -> str:
        """Generate recommendations based on results"""
        scores = [int(r['score'].split('/')[0]) for r in results if r.get('score')]
        avg = sum(scores) / len(scores) if scores else 0
        
        # Count failed criteria across all requirements
        failed_counts = {}
        for r in results:
            evaluation = r.get('evaluation', {})
            if isinstance(evaluation, dict):
                for criterion in evaluation.keys():
                    if criterion != 'error':
                        failed_counts[criterion] = failed_counts.get(criterion, 0) + 1
        
        # Get most common failures
        if failed_counts:
            top_failures = sorted(
                failed_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
            top_3 = ", ".join([f"{c} ({n} ข้อ)" for c, n in top_failures])
            
            return f"คะแนนเฉลี่ย {avg:.1f}/9 | ปัญหาที่พบบ่อยสุด: {top_3}"
        
        if avg >= 8:
            return f"คะแนนเฉลี่ย {avg:.1f}/9 | คุณภาพดีมาก ผ่านเกณฑ์มาตรฐาน"
        elif avg >= 6:
            return f"คะแนนเฉลี่ย {avg:.1f}/9 | คุณภาพดี มีบางข้อควรปรับปรุง"
        elif avg >= 4:
            return f"คะแนนเฉลี่ย {avg:.1f}/9 | ต้องปรับปรุงในหลายด้าน"
        else:
            return f"คะแนนเฉลี่ย {avg:.1f}/9 | ต้องเขียนใหม่อย่างเร่งด่วน"
    
    async def analyze_with_progress(
        self,
        requirements: List[Dict],
        requirement_template: str = "Others",
        websocket=None,
        reference_context: str = None,
        enabled_criteria: list = None,
    ):
        """
        Analyze with real-time progress updates via WebSocket
        """
        total = len(requirements)

        import asyncio

        async def safe_send(data: dict) -> None:
            if websocket:
                try:
                    await websocket.send_json(data)
                except Exception:
                    pass

        async def progress_callback(completed, total):
            await safe_send({
                "type": "progress",
                "completed": completed,
                "total": total,
                "percentage": (completed / total) * 100
            })

        heartbeat_stop = asyncio.Event()

        async def heartbeat():
            while not heartbeat_stop.is_set():
                await asyncio.sleep(10)
                if not heartbeat_stop.is_set():
                    await safe_send({"type": "heartbeat"})

        heartbeat_task = asyncio.create_task(heartbeat())
        try:
            result = await self.analyze_requirements_parallel(
                requirements,
                requirement_template,
                progress_callback=progress_callback,
                reference_context=reference_context,
                enabled_criteria=enabled_criteria,
            )
        finally:
            heartbeat_stop.set()
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass

        await safe_send({"type": "complete", "result": result})

        return result
    
    def _generate_suggestion_for_requirement(
        self,
        req_id: str,
        requirement: str,
        evaluation: Dict[str, str],
        module: str = None,
        requirement_template: str = "Others",
        min_similarity: float = 0.5,
        max_retries: int = 3,
    ) -> Dict:
        """
        Generate improved requirement based on failed criteria.
        Uses Gemini AI classification to find relevant ISO 29148 rules from DB.
        """
        # Helper: extract reason string from evaluation value (supports both str and {reason, cited_rules})
        def _reason_str(v) -> str:
            if isinstance(v, dict):
                return v.get("reason", "") or ""
            return str(v) if v else ""

        # Split evaluation into actual FAILs vs CANNOT_DETERMINE (prefixed with "[?]")
        actually_failed = {
            k: v for k, v in evaluation.items()
            if k != 'error' and not _reason_str(v).startswith('[?]')
        }
        cannot_determine = {
            k: v for k, v in evaluation.items()
            if k != 'error' and _reason_str(v).startswith('[?]')
        }

        # If nothing actually failed (all CANNOT_DETERMINE), nothing to improve
        if not actually_failed:
            return {
                "req_id": req_id,
                "is_split": False,
                "suggested_requirement": requirement,
                "split_requirements": None,
                "improvements": {},
                "explanation": "ไม่มี criteria ที่ FAIL จริง — criteria ที่ไม่ผ่านทั้งหมดเป็น CANNOT_DETERMINE เนื่องจากขาดข้อมูลอ้างอิง",
                "success": True,
            }

        # Check if "Singular" is in actually failed criteria (not CANNOT_DETERMINE)
        has_singular_failure = "Singular" in actually_failed

        # Build context about actually failed criteria only
        failed_criteria_text = "\n".join([
            f"- {criterion}: {_reason_str(reason)}"
            for criterion, reason in actually_failed.items()
        ])

        # Note about skipped CANNOT_DETERMINE criteria
        cannot_determine_note = ""
        if cannot_determine:
            skipped = ", ".join(cannot_determine.keys())
            cannot_determine_note = f"\nNOTE: The following criteria were CANNOT_DETERMINE during analysis (no reference documents available) and must NOT be modified or assumed: {skipped}. Leave them as-is."

        # Build rules reference for all failed criteria
        all_failed_criteria = list(actually_failed.keys())
        relevant_rule_names: List[str] = []
        for c in all_failed_criteria:
            for rn in self.RULES_BY_CRITERION.get(c, []):
                if rn not in relevant_rule_names:
                    relevant_rule_names.append(rn)
        rules_lookup = {r["name"]: r for r in self.RULES}
        suggestion_rules_block = ""
        if relevant_rule_names:
            lines = [f'- "{rn}" (§{rules_lookup[rn]["section"]}): {rules_lookup[rn]["description"]}'
                     for rn in relevant_rule_names if rn in rules_lookup]
            if lines:
                suggestion_rules_block = "\nReference rules (cite in cited_rules per criterion):\n" + "\n".join(lines)

        # Build template context (patterns only — name/description not needed in prompt)
        template_info = self.TEMPLATE_DEFINITIONS.get(requirement_template, self.TEMPLATE_DEFINITIONS["Others"])
        template_patterns = template_info['patterns']

        # EARS Thai translation hint — only relevant when template is EARS
        ears_hint = ""
        if requirement_template == "EARS":
            ears_hint = "If writing in Thai, use EARS keywords: เมื่อ (WHEN), ในขณะที่ (WHILE), ถ้า (IF), ในกรณีที่ (WHERE), ต้อง (shall), ระบบ (system)."

        # List other failing criteria besides Singular (for split case)
        other_failed_criteria = {k: v for k, v in evaluation.items() if k != "Singular" and k != "error"}
        other_failed_text = "\n".join([
            f"  - {criterion}: {_reason_str(reason)}"
            for criterion, reason in other_failed_criteria.items()
        ]) if other_failed_criteria else "  (none)"

        # Split vs rewrite instruction
        singular_reason = _reason_str(evaluation.get("Singular", ""))
        if has_singular_failure:
            action_instruction = f"""ACTION: SPLIT
The requirement mixes multiple capabilities. Split into one requirement per capability.
Singular failure reason: "{singular_reason}"

Split rules:
- Produce MINIMUM 2 requirements; if only 1 is possible → set is_split:false and rewrite instead
- Broad terms like "management/capabilities/operations" → split into standard CRUD-like sub-functions
- Do NOT invent actors/triggers/mechanisms not stated; domain-standard sub-functions are allowed
- Also fix these other failed criteria in EACH split: {other_failed_text if other_failed_text.strip() else "(none)"}
- req_id format: {req_id}-1, {req_id}-2, ..."""
        else:
            action_instruction = "ACTION: REWRITE (do NOT split — is_split must be false)"

        req_lang = self._detect_language(requirement)
        if req_lang == "Thai":
            if requirement_template == "EARS":
                lang_hint = "If writing in Thai, use EARS keywords: เมื่อ (WHEN), ในขณะที่ (WHILE), ถ้า (IF), ในกรณีที่ (WHERE), ต้อง (shall), ระบบ (system)."
            elif requirement_template == "ISO29148":
                lang_hint = (
                    "IMPORTANT: The requirement is in Thai. Do NOT use English words like 'shall', 'should', 'must', 'will' in the output. "
                    "Replace them with Thai equivalents: 'shall' → 'ต้อง', 'should' → 'ควร'. "
                    "Write the entire suggested_requirement in Thai only."
                )
            else:
                lang_hint = "IMPORTANT: The requirement is in Thai. Write the entire suggested_requirement in Thai only. Do not include any English words in the requirement text."
        else:
            lang_hint = ears_hint

        no_english_in_req = (
            "\nCRITICAL: The suggested_requirement and all requirement text MUST be written entirely in Thai. "
            "Do NOT insert any English words (including 'shall', 'should', 'must', 'will', 'WHEN', 'WHILE', 'IF', 'WHERE') into the requirement text. "
            "Use only Thai vocabulary."
        ) if req_lang == "Thai" else ""

        prompt = f"""You are a software requirement expert. Improve the requirement below to fix ALL listed failed criteria.

OUTPUT LANGUAGE: {req_lang}. Every text field in your JSON response (suggested_requirement, requirement in split_requirements, description in improvements, explanation) MUST be written in {req_lang} only. Do not use any other language.
{lang_hint}{no_english_in_req}

Requirement: "{requirement}" (ID: {req_id}, Module: {module or 'N/A'})

Failed criteria to fix:
{failed_criteria_text}
{cannot_determine_note}
Template ({requirement_template}):
{template_patterns}
{action_instruction}
{suggestion_rules_block}
Constraints:
- Fix ONLY what failed; preserve original intent and level of detail
- Do NOT invent values, thresholds, timings, mechanisms, actors, or outcomes not in the original (e.g., do not add "15 minutes", "mouse input", "redirect to login")
- If a criterion cannot be fixed without fabricating info, improve wording/structure only
- Plain text output — no markdown, no bullet characters inside requirement text
- All output text MUST be in {req_lang}

Return JSON only:
{{
  "req_id": "{req_id}",
  "is_split": true|false,
  "suggested_requirement": "<plain text (when is_split=false, else null)>",
  "split_requirements": [
    {{
      "req_id": "{req_id}-1",
      "requirement": "<plain text, single capability>",
      "module": "<module>"
    }}
  ],
  "improvements": {{
    "<criterion>": {{
      "description": "<explanation of what was changed and why — e.g. 'Replaced \"will\" with \"shall\" to make the obligation mandatory. Restructured using EARS Event-driven pattern: WHEN [trigger], the system shall [action].' Do NOT include ISO section numbers or standard citations.>",
      "cited_rules": ["<rule name>"]
    }}
  }},
  "explanation": "<brief overall summary>"
}}
split_requirements is null when is_split=false.
cited_rules per improvement: list rule names from the reference above that motivated the fix (empty list [] if none apply).
description per improvement: explain what was changed and why it fixes the issue. Do NOT mention ISO section numbers (§5.2.x) or standard names in the description text.
Output JSON only."""
        
        best_result = None
        best_sim = -1.0

        for attempt in range(max_retries + 1):
            retry_note = (
                f"\n\nIMPORTANT (retry {attempt}/{max_retries}): The previous version had low semantic "
                "similarity with the original requirement. Preserve the core meaning, domain terms, and "
                "structure of the original as closely as possible while fixing only the failed criteria."
            ) if attempt > 0 else ""

            try:
                result_text = self.llm.generate_json(prompt + retry_note)

                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0].strip()

                data = json.loads(result_text)

                all_improvements = data.get("improvements", {})
                failed_criteria_only = {}
                for criterion, improvement in all_improvements.items():
                    if criterion not in evaluation:
                        continue
                    if isinstance(improvement, dict):
                        failed_criteria_only[criterion] = {
                            "description": improvement.get("description", ""),
                            "cited_rules": improvement.get("cited_rules") or [],
                        }
                    else:
                        failed_criteria_only[criterion] = {
                            "description": str(improvement),
                            "cited_rules": [],
                        }

                is_split = data.get("is_split", False)
                split_requirements = data.get("split_requirements") or None
                suggested_requirement = data.get("suggested_requirement") or ""

                if not has_singular_failure and is_split:
                    is_split = False
                    if not suggested_requirement and split_requirements:
                        suggested_requirement = split_requirements[0].get("requirement", "") or ""
                    split_requirements = None

                if is_split and (not split_requirements or len(split_requirements) < 2):
                    is_split = False
                    if split_requirements and len(split_requirements) == 1:
                        suggested_requirement = split_requirements[0].get("requirement", "") or suggested_requirement
                    split_requirements = None

                # Compute semantic similarity to decide whether to retry
                if is_split and split_requirements:
                    suggested_text = ' '.join(s.get('requirement', '') for s in split_requirements)
                else:
                    suggested_text = suggested_requirement or ''

                sim = _sem_sim(requirement, suggested_text) if suggested_text else 0.0

                current_result = {
                    "req_id": req_id,
                    "is_split": is_split,
                    "suggested_requirement": suggested_requirement if not is_split else None,
                    "split_requirements": split_requirements if is_split else None,
                    "improvements": failed_criteria_only,
                    "explanation": data.get("explanation", ""),
                    "success": True,
                    "semantic_similarity": sim,
                }

                if best_result is None or sim > best_sim:
                    best_sim = sim
                    best_result = current_result

                if sim >= min_similarity or not suggested_text:
                    break

                logger.info(
                    f"[suggestion_retry] {req_id}: attempt {attempt + 1}/{max_retries + 1} "
                    f"sem_sim={sim:.3f} < threshold {min_similarity}, retrying..."
                )

            except Exception as e:
                logger.error(f"[suggestion_retry] {req_id}: attempt {attempt + 1} exception: {e}")
                if best_result is None:
                    best_result = {
                        "req_id": req_id,
                        "is_split": False,
                        "suggested_requirement": "",
                        "split_requirements": None,
                        "improvements": {},
                        "explanation": f"เกิดข้อผิดพลาด: {str(e)}",
                        "success": False,
                        "error": str(e)
                    }
                break

        return best_result
    
    async def generate_suggestions_parallel(
        self,
        analyzed_requirements: List[Dict],
        progress_callback=None,
        min_similarity: float = 0.5,
        max_retries: int = 3,
    ) -> Dict:
        """
        Generate suggestions for multiple requirements in parallel
        Only processes requirements with score < 9/9
        """
        # Filter requirements that need improvement (score < 9/9)
        needs_improvement = []
        already_perfect = []
        
        for req in analyzed_requirements:
            score = req.get('score', '0/9')
            current_score = int(score.split('/')[0]) if score else 0
            
            if current_score < 9:
                needs_improvement.append(req)
            else:
                already_perfect.append(req)
        
        if not needs_improvement:
            return {
                "results": [],
                "summary": {
                    "total_analyzed": len(analyzed_requirements),
                    "needs_improvement": 0,
                    "already_perfect": len(already_perfect),
                    "suggestions_generated": 0,
                    "message": "ทุก requirement ผ่านเกณฑ์ครบ 9/9 แล้ว ไม่จำเป็นต้อง suggest"
                }
            }
        
        total = len(needs_improvement)
        results = []
        
        # Create async tasks
        loop = asyncio.get_event_loop()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            futures = [
                loop.run_in_executor(
                    executor,
                    self._generate_suggestion_for_requirement,
                    req['req_id'],
                    req['requirement'],
                    req.get('evaluation', {}),
                    req.get('module'),
                    req.get('requirement_template', 'Others'),
                    min_similarity,
                    max_retries,
                )
                for req in needs_improvement
            ]
            
            # Process as they complete
            completed = 0
            for future in asyncio.as_completed(futures):
                result = await future
                results.append(result)
                completed += 1
                
                # Progress callback
                if progress_callback:
                    await progress_callback(completed, total)
        
        successful = sum(1 for r in results if r.get('success', False))
        
        return {
            "results": results,
            "summary": {
                "total_analyzed": len(analyzed_requirements),
                "needs_improvement": len(needs_improvement),
                "already_perfect": len(already_perfect),
                "suggestions_generated": successful,
                "failed": len(results) - successful,
                "message": f"สร้าง suggestion สำเร็จ {successful}/{len(needs_improvement)} ข้อ"
            }
        }
    
    def generate_suggestions_parallel_sync(
        self,
        analyzed_requirements: List[Dict],
        min_similarity: float = 0.5,
        max_retries: int = 3,
    ) -> Dict:
        return asyncio.run(self.generate_suggestions_parallel(
            analyzed_requirements,
            min_similarity=min_similarity,
            max_retries=max_retries,
        ))
    
    async def generate_suggestion_with_progress(
        self,
        analyzed_requirements: List[Dict],
        websocket=None,
        min_similarity: float = 0.5,
        max_retries: int = 3,
    ):
        """
        Generate suggestions with real-time progress updates via WebSocket
        """
        async def safe_send(data: dict) -> None:
            if websocket:
                try:
                    await websocket.send_json(data)
                except Exception:
                    pass

        async def progress_callback(completed, total):
            await safe_send({
                "type": "progress",
                "completed": completed,
                "total": total,
                "percentage": (completed / total) * 100
            })

        result = await self.generate_suggestions_parallel(
            analyzed_requirements,
            progress_callback=progress_callback,
            min_similarity=min_similarity,
            max_retries=max_retries,
        )

        await safe_send({"type": "complete", "result": result})

        return result