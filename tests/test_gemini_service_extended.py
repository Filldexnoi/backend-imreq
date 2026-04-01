"""
Extended tests for services/gemini_service.py
Covers: _extract_reference_text, _build_rules_reference, _analyze_single_criterion,
        _analyze_single_requirement_all_criteria, _generate_recommendations,
        _generate_suggestion_for_requirement, generate_suggestions_parallel,
        analyze_requirements_parallel, analyze_with_progress,
        generate_suggestion_with_progress
"""
import base64
import io
import json
import asyncio
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.gemini_service import GeminiService


# ---------------------------------------------------------------------------
# Fixture: GeminiService instance with mocked genai client
# ---------------------------------------------------------------------------

@pytest.fixture
def svc():
    """GeminiService with mocked OpenAI client."""
    with patch("os.getenv", return_value="fake-key"), \
         patch("services.gemini_service.OpenAI") as mock_openai:
        mock_openai.return_value = MagicMock()
        s = GeminiService(max_workers=2)
    return s


def _fake_response(text: str):
    """Simulate OpenAI chat completion response."""
    msg = MagicMock()
    msg.content = text
    choice = MagicMock()
    choice.message = msg
    r = MagicMock()
    r.choices = [choice]
    return r


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------

class TestInit:
    def test_missing_api_key_raises(self):
        with patch("services.gemini_service.os.getenv", return_value=None):
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                GeminiService()


# ---------------------------------------------------------------------------
# _extract_reference_text
# ---------------------------------------------------------------------------

class TestExtractReferenceText:
    def test_empty_list_returns_none(self, svc):
        assert svc._extract_reference_text([]) is None

    def test_txt_file(self, svc):
        content = b"Hello world requirements."
        b64 = base64.b64encode(content).decode()
        result = svc._extract_reference_text([{
            "name": "req.txt", "content": b64, "type": "text/plain"
        }])
        assert "Hello world" in result

    def test_markdown_file(self, svc):
        content = b"# Requirements\nThe system shall..."
        b64 = base64.b64encode(content).decode()
        result = svc._extract_reference_text([{
            "name": "req.md", "content": b64, "type": "text/markdown"
        }])
        assert "Requirements" in result

    def test_txt_by_extension(self, svc):
        content = b"Text by extension."
        b64 = base64.b64encode(content).decode()
        result = svc._extract_reference_text([{
            "name": "notes.txt", "content": b64, "type": "application/octet-stream"
        }])
        assert "Text by extension" in result

    def test_unsupported_type_skipped(self, svc):
        b64 = base64.b64encode(b"data").decode()
        result = svc._extract_reference_text([{
            "name": "image.png", "content": b64, "type": "image/png"
        }])
        assert result is None

    def test_extraction_exception_skipped(self, svc):
        # invalid base64 → exception → skip
        result = svc._extract_reference_text([{
            "name": "broken.txt", "content": "!!!not_base64!!!", "type": "text/plain"
        }])
        assert result is None

    def test_multiple_files_combined(self, svc):
        c1 = base64.b64encode(b"File one.").decode()
        c2 = base64.b64encode(b"File two.").decode()
        result = svc._extract_reference_text([
            {"name": "a.txt", "content": c1, "type": "text/plain"},
            {"name": "b.txt", "content": c2, "type": "text/plain"},
        ])
        assert "File one" in result
        assert "File two" in result

    def test_truncation_at_10000_chars(self, svc):
        big_text = "x" * 15000
        b64 = base64.b64encode(big_text.encode()).decode()
        result = svc._extract_reference_text([{
            "name": "big.txt", "content": b64, "type": "text/plain"
        }])
        assert len(result) <= 10100
        assert "[truncated]" in result

    def test_pdf_file(self, svc):
        content = b"fake pdf bytes"
        b64 = base64.b64encode(content).decode()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "PDF page text"
        mock_pdf_ctx = MagicMock()
        mock_pdf_ctx.__enter__ = lambda s: mock_pdf_ctx
        mock_pdf_ctx.__exit__ = MagicMock(return_value=False)
        mock_pdf_ctx.pages = [mock_page]
        mock_pdfplumber = MagicMock()
        mock_pdfplumber.open.return_value = mock_pdf_ctx
        with patch.dict(sys.modules, {"pdfplumber": mock_pdfplumber}):
            result = svc._extract_reference_text([{
                "name": "doc.pdf", "content": b64, "type": "application/pdf"
            }])
        assert "PDF page text" in result

    def test_docx_file(self, svc):
        content = b"fake docx bytes"
        b64 = base64.b64encode(content).decode()
        mock_para = MagicMock()
        mock_para.text = "Docx paragraph text"
        mock_doc_obj = MagicMock()
        mock_doc_obj.paragraphs = [mock_para]
        mock_docx = MagicMock()
        mock_docx.Document.return_value = mock_doc_obj
        with patch.dict(sys.modules, {"docx": mock_docx}):
            result = svc._extract_reference_text([{
                "name": "req.docx", "content": b64,
                "type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            }])
        assert "Docx paragraph" in result


# ---------------------------------------------------------------------------
# _build_rules_reference
# ---------------------------------------------------------------------------

class TestBuildRulesReference:
    def test_criterion_with_rules(self, svc):
        result = svc._build_rules_reference("Conforming")
        assert "Reference rules" in result
        assert "shall" in result.lower()

    def test_criterion_without_rules(self, svc):
        result = svc._build_rules_reference("Correct")
        assert result == ""

    def test_unknown_criterion(self, svc):
        result = svc._build_rules_reference("NonExistent")
        assert result == ""


# ---------------------------------------------------------------------------
# _analyze_single_criterion
# ---------------------------------------------------------------------------

class TestAnalyzeSingleCriterion:
    def _mock_response(self, svc, text):
        svc.client.chat.completions.create.return_value = _fake_response(text)

    def test_plain_json_response(self, svc):
        payload = json.dumps({
            "criterion": "Appropriate",
            "status": "PASS",
            "reason": "Looks good.",
            "cited_rules": []
        })
        self._mock_response(svc, payload)
        result = svc._analyze_single_criterion("Appropriate", "The system shall X.", "REQ-001")
        assert result["status"] == "PASS"
        assert result["criterion"] == "Appropriate"

    def test_json_fenced_response(self, svc):
        payload = json.dumps({"criterion": "Complete", "status": "FAIL",
                               "reason": "Missing subject.", "cited_rules": ["Formal Syntax"]})
        self._mock_response(svc, f"```json\n{payload}\n```")
        result = svc._analyze_single_criterion("Complete", "Shall do X.", "REQ-002")
        assert result["status"] == "FAIL"
        assert "Formal Syntax" in result["cited_rules"]

    def test_backtick_fenced_response(self, svc):
        payload = json.dumps({"criterion": "Singular", "status": "FAIL",
                               "reason": "Multiple capabilities.", "cited_rules": []})
        self._mock_response(svc, f"```\n{payload}\n```")
        result = svc._analyze_single_criterion("Singular", "Shall A and B.", "REQ-003")
        assert result["status"] == "FAIL"

    def test_exception_returns_fail(self, svc):
        svc.client.chat.completions.create.side_effect = Exception("API down")
        result = svc._analyze_single_criterion("Verifiable", "Shall respond quickly.", "REQ-004")
        assert result["status"] == "FAIL"
        assert "criterion" in result

    def test_conforming_with_template(self, svc):
        payload = json.dumps({"criterion": "Conforming", "status": "PASS",
                               "reason": "Uses shall.", "cited_rules": [],
                               "detected_pattern": "ISO29148: Standard"})
        self._mock_response(svc, payload)
        result = svc._analyze_single_criterion(
            "Conforming", "The system shall X.", "REQ-005",
            requirement_template="ISO29148"
        )
        assert result["detected_pattern"] == "ISO29148: Standard"

    def test_criterion_with_ref_block(self, svc):
        payload = json.dumps({"criterion": "Correct", "status": "PASS",
                               "reason": "Matches reference.", "cited_rules": []})
        self._mock_response(svc, payload)
        result = svc._analyze_single_criterion(
            "Correct", "System shall login.", "REQ-006",
            reference_context="User must be able to log in."
        )
        assert result["status"] == "PASS"

    def test_cannot_determine(self, svc):
        payload = json.dumps({"criterion": "Necessary", "status": "CANNOT_DETERMINE",
                               "reason": "No reference.", "cited_rules": []})
        self._mock_response(svc, payload)
        result = svc._analyze_single_criterion("Necessary", "System shall support X.", "REQ-007")
        assert result["status"] == "CANNOT_DETERMINE"


# ---------------------------------------------------------------------------
# _analyze_single_requirement_all_criteria
# ---------------------------------------------------------------------------

class TestAnalyzeSingleRequirementAllCriteria:
    def _mock_all_criteria(self, svc, status="PASS"):
        def fake_analyze(criterion, requirement, req_id, *args, **kwargs):
            return {
                "criterion": criterion,
                "status": status,
                "reason": "reason",
                "cited_rules": [],
                "detected_pattern": None,
            }
        svc._analyze_single_criterion = fake_analyze

    def test_all_pass(self, svc):
        self._mock_all_criteria(svc, "PASS")
        result = svc._analyze_single_requirement_all_criteria(
            "The system shall X.", "REQ-001"
        )
        assert result["score"] == "9/9"
        assert len(result["characteristics"]) == 9
        assert result["evaluation"] == {}

    def test_all_fail(self, svc):
        self._mock_all_criteria(svc, "FAIL")
        result = svc._analyze_single_requirement_all_criteria(
            "Do something.", "REQ-002"
        )
        assert result["score"] == "0/9"
        assert len(result["evaluation"]) == 9

    def test_all_cannot_determine(self, svc):
        def fake(criterion, requirement, req_id, *args, **kwargs):
            return {"criterion": criterion, "status": "CANNOT_DETERMINE",
                    "reason": "no context", "cited_rules": [], "detected_pattern": None}
        svc._analyze_single_criterion = fake
        result = svc._analyze_single_requirement_all_criteria(
            "System shall handle users.", "REQ-003"
        )
        assert result["score"] == "0/9"
        for reason_data in result["evaluation"].values():
            assert "[?]" in reason_data["reason"]

    def test_conforming_adds_template_prefix(self, svc):
        def fake(criterion, requirement, req_id, requirement_template="Others",
                 reference_context=None):
            status = "FAIL" if criterion == "Conforming" else "PASS"
            return {"criterion": criterion, "status": status,
                    "reason": "missing shall", "cited_rules": [], "detected_pattern": None}
        svc._analyze_single_criterion = fake
        result = svc._analyze_single_requirement_all_criteria(
            "Requirement text.", "REQ-004", requirement_template="EARS"
        )
        assert "[Template: EARS]" in result["evaluation"]["Conforming"]["reason"]

    def test_mixed_results(self, svc):
        pass_set = {"Appropriate", "Complete", "Conforming"}
        def fake(criterion, requirement, req_id, *args, **kwargs):
            status = "PASS" if criterion in pass_set else "FAIL"
            return {"criterion": criterion, "status": status,
                    "reason": "reason", "cited_rules": [], "detected_pattern": None}
        svc._analyze_single_criterion = fake
        result = svc._analyze_single_requirement_all_criteria("Req.", "REQ-005")
        assert result["score"] == "3/9"
        assert len(result["characteristics"]) == 3


# ---------------------------------------------------------------------------
# _generate_recommendations
# ---------------------------------------------------------------------------

class TestGenerateRecommendations:
    def _make_results(self, scores, evaluations=None):
        results = []
        for i, score in enumerate(scores):
            results.append({
                "score": f"{score}/9",
                "evaluation": evaluations[i] if evaluations else {}
            })
        return results

    def test_with_failed_criteria(self, svc):
        results = self._make_results(
            [5, 6, 4],
            [{"Unambiguous": "vague"}, {"Unambiguous": "vague"}, {"Complete": "missing"}]
        )
        rec = svc._generate_recommendations(results)
        assert "Unambiguous" in rec

    def test_high_avg(self, svc):
        results = self._make_results([9, 8, 9])
        rec = svc._generate_recommendations(results)
        assert "ดีมาก" in rec

    def test_good_avg(self, svc):
        results = self._make_results([7, 6, 7])
        rec = svc._generate_recommendations(results)
        assert "ดี" in rec

    def test_medium_avg(self, svc):
        results = self._make_results([4, 5, 4])
        rec = svc._generate_recommendations(results)
        assert "ปรับปรุง" in rec

    def test_low_avg(self, svc):
        results = self._make_results([1, 2, 1])
        rec = svc._generate_recommendations(results)
        assert "ใหม่" in rec

    def test_empty_results(self, svc):
        rec = svc._generate_recommendations([])
        assert isinstance(rec, str)


# ---------------------------------------------------------------------------
# _generate_suggestion_for_requirement
# ---------------------------------------------------------------------------

class TestGenerateSuggestionForRequirement:
    def _mock_llm(self, svc, payload: dict):
        svc.client.chat.completions.create.return_value = _fake_response(json.dumps(payload))

    def test_all_cannot_determine_returns_original(self, svc):
        evaluation = {
            "Necessary": {"reason": "[?] no reference doc", "cited_rules": []},
            "Correct":   {"reason": "[?] no reference doc", "cited_rules": []},
        }
        result = svc._generate_suggestion_for_requirement(
            "REQ-001", "The system shall do X.", evaluation
        )
        assert result["success"] is True
        assert result["suggested_requirement"] == "The system shall do X."
        assert result["improvements"] == {}

    def test_fail_rewrite(self, svc):
        evaluation = {"Unambiguous": {"reason": "vague", "cited_rules": []}}
        payload = {
            "req_id": "REQ-001",
            "is_split": False,
            "suggested_requirement": "The system shall respond within 2 seconds.",
            "split_requirements": None,
            "improvements": {
                "Unambiguous": {"description": "Removed vague term.", "cited_rules": []}
            },
            "explanation": "Fixed vague wording."
        }
        self._mock_llm(svc, payload)
        result = svc._generate_suggestion_for_requirement(
            "REQ-001", "System shall be fast.", evaluation
        )
        assert result["success"] is True
        assert result["is_split"] is False
        assert "respond within" in result["suggested_requirement"]

    def test_fail_split(self, svc):
        evaluation = {"Singular": {"reason": "Two capabilities joined.", "cited_rules": []}}
        payload = {
            "req_id": "REQ-001",
            "is_split": True,
            "suggested_requirement": None,
            "split_requirements": [
                {"req_id": "REQ-001-1", "requirement": "System shall do A.", "module": "M"},
                {"req_id": "REQ-001-2", "requirement": "System shall do B.", "module": "M"},
            ],
            "improvements": {
                "Singular": {"description": "Split into two.", "cited_rules": []}
            },
            "explanation": "Split requirement."
        }
        self._mock_llm(svc, payload)
        result = svc._generate_suggestion_for_requirement(
            "REQ-001", "System shall A and B.", evaluation
        )
        assert result["is_split"] is True
        assert len(result["split_requirements"]) == 2

    def test_guard_singular_not_failed_but_llm_splits(self, svc):
        """Server-side guard: Singular not in failed → force is_split=False."""
        evaluation = {"Unambiguous": {"reason": "vague", "cited_rules": []}}
        payload = {
            "req_id": "REQ-001",
            "is_split": True,  # LLM wrongly split
            "suggested_requirement": None,
            "split_requirements": [
                {"req_id": "REQ-001-1", "requirement": "A.", "module": "M"},
                {"req_id": "REQ-001-2", "requirement": "B.", "module": "M"},
            ],
            "improvements": {},
            "explanation": "Split."
        }
        self._mock_llm(svc, payload)
        result = svc._generate_suggestion_for_requirement(
            "REQ-001", "System shall be user-friendly.", evaluation
        )
        assert result["is_split"] is False
        assert result["split_requirements"] is None

    def test_guard_split_less_than_2(self, svc):
        """Server-side guard: split produces only 1 item → demote to rewrite."""
        evaluation = {"Singular": {"reason": "Two capabilities.", "cited_rules": []}}
        payload = {
            "req_id": "REQ-001",
            "is_split": True,
            "suggested_requirement": None,
            "split_requirements": [
                {"req_id": "REQ-001-1", "requirement": "System shall do A.", "module": "M"},
            ],
            "improvements": {},
            "explanation": "Only one split."
        }
        self._mock_llm(svc, payload)
        result = svc._generate_suggestion_for_requirement(
            "REQ-001", "System shall A and B.", evaluation
        )
        assert result["is_split"] is False
        assert result["split_requirements"] is None

    def test_exception_returns_error(self, svc):
        evaluation = {"Unambiguous": {"reason": "vague", "cited_rules": []}}
        svc.client.chat.completions.create.side_effect = Exception("Network error")
        result = svc._generate_suggestion_for_requirement(
            "REQ-001", "Shall be good.", evaluation
        )
        assert result["success"] is False
        assert "error" in result

    def test_json_fenced_response(self, svc):
        evaluation = {"Complete": {"reason": "Missing action.", "cited_rules": []}}
        payload = {
            "req_id": "REQ-001", "is_split": False,
            "suggested_requirement": "System shall process requests.",
            "split_requirements": None,
            "improvements": {"Complete": {"description": "Added action.", "cited_rules": []}},
            "explanation": "Fixed."
        }
        svc.client.chat.completions.create.return_value = _fake_response(
            f"```json\n{json.dumps(payload)}\n```"
        )
        result = svc._generate_suggestion_for_requirement("REQ-001", "System shall.", evaluation)
        assert result["success"] is True

    def test_plain_string_improvement_normalised(self, svc):
        """LLM returns plain string as improvement value (old format)."""
        evaluation = {"Unambiguous": {"reason": "vague", "cited_rules": []}}
        payload = {
            "req_id": "REQ-001", "is_split": False,
            "suggested_requirement": "System shall respond in 2s.",
            "split_requirements": None,
            "improvements": {"Unambiguous": "Replaced vague with metric."},
            "explanation": "Fixed."
        }
        self._mock_llm(svc, payload)
        result = svc._generate_suggestion_for_requirement(
            "REQ-001", "System shall be fast.", evaluation
        )
        assert result["success"] is True
        assert isinstance(result["improvements"]["Unambiguous"], dict)


# ---------------------------------------------------------------------------
# generate_suggestions_parallel
# ---------------------------------------------------------------------------

class TestGenerateSuggestionsParallel:
    def test_all_perfect_skips_generation(self, svc):
        reqs = [
            {"req_id": "REQ-001", "requirement": "...", "score": "9/9", "evaluation": {}},
            {"req_id": "REQ-002", "requirement": "...", "score": "9/9", "evaluation": {}},
        ]
        result = asyncio.run(svc.generate_suggestions_parallel(reqs))
        assert result["results"] == []
        assert result["summary"]["already_perfect"] == 2

    def test_generates_for_imperfect(self, svc):
        reqs = [
            {"req_id": "REQ-001", "requirement": "Shall do X.", "score": "5/9",
             "evaluation": {"Unambiguous": "vague"}, "module": "M", "requirement_template": "Others"},
        ]
        fake = {
            "req_id": "REQ-001", "is_split": False,
            "suggested_requirement": "System shall do X clearly.",
            "split_requirements": None,
            "improvements": {"Unambiguous": {"description": "Fixed.", "cited_rules": []}},
            "explanation": "Improved.", "success": True
        }
        svc._generate_suggestion_for_requirement = MagicMock(return_value=fake)
        result = asyncio.run(svc.generate_suggestions_parallel(reqs))
        assert len(result["results"]) == 1
        assert result["summary"]["suggestions_generated"] == 1

    def test_mixed_perfect_and_imperfect(self, svc):
        reqs = [
            {"req_id": "REQ-001", "requirement": "Req 1.", "score": "9/9", "evaluation": {}},
            {"req_id": "REQ-002", "requirement": "Req 2.", "score": "4/9",
             "evaluation": {"Complete": "missing"}, "module": None, "requirement_template": "Others"},
        ]
        fake = {
            "req_id": "REQ-002", "is_split": False,
            "suggested_requirement": "Fixed req.",
            "split_requirements": None, "improvements": {}, "explanation": "", "success": True
        }
        svc._generate_suggestion_for_requirement = MagicMock(return_value=fake)
        result = asyncio.run(svc.generate_suggestions_parallel(reqs))
        assert result["summary"]["already_perfect"] == 1
        assert result["summary"]["needs_improvement"] == 1

    def test_with_progress_callback(self, svc):
        reqs = [
            {"req_id": "REQ-001", "requirement": "Req.", "score": "5/9",
             "evaluation": {"Verifiable": "no metric"}, "module": None, "requirement_template": "Others"},
        ]
        fake = {
            "req_id": "REQ-001", "is_split": False, "suggested_requirement": "Fixed.",
            "split_requirements": None, "improvements": {}, "explanation": "", "success": True
        }
        svc._generate_suggestion_for_requirement = MagicMock(return_value=fake)
        callbacks = []
        async def cb(completed, total):
            callbacks.append((completed, total))
        result = asyncio.run(svc.generate_suggestions_parallel(reqs, progress_callback=cb))
        assert len(callbacks) == 1


# ---------------------------------------------------------------------------
# analyze_requirements_parallel
# ---------------------------------------------------------------------------

class TestAnalyzeRequirementsParallel:
    def test_basic_parallel_analysis(self, svc):
        reqs = [
            {"req_id": "REQ-001", "requirement": "The system shall X.", "module": "M"},
            {"req_id": "REQ-002", "requirement": "The system shall Y.", "module": "M"},
        ]
        fake = {
            "req_id": "REQ-001", "score": "7/9",
            "characteristics": ["Appropriate"], "evaluation": {}, "detailed_results": []
        }
        def fake_analyze(req, req_id, *args, **kwargs):
            return {**fake, "req_id": req_id}
        svc._analyze_single_requirement_all_criteria = fake_analyze
        result = asyncio.run(svc.analyze_requirements_parallel(reqs))
        assert len(result["results"]) == 2
        assert "summary" in result
        assert "average_score" in result["summary"]

    def test_with_progress_callback(self, svc):
        reqs = [{"req_id": "REQ-001", "requirement": "Req.", "module": "M"}]
        svc._analyze_single_requirement_all_criteria = lambda r, rid, *a, **kw: {
            "req_id": rid, "score": "9/9", "characteristics": [], "evaluation": {}, "detailed_results": []
        }
        callbacks = []
        async def cb(c, t): callbacks.append((c, t))
        result = asyncio.run(svc.analyze_requirements_parallel(reqs, progress_callback=cb))
        assert len(callbacks) == 1


# ---------------------------------------------------------------------------
# analyze_with_progress
# ---------------------------------------------------------------------------

class TestAnalyzeWithProgress:
    def test_sends_complete_to_websocket(self, svc):
        reqs = [{"req_id": "REQ-001", "requirement": "Req.", "module": "M"}]
        svc._analyze_single_requirement_all_criteria = lambda r, rid, *a, **kw: {
            "req_id": rid, "score": "8/9", "characteristics": [], "evaluation": {}, "detailed_results": []
        }
        ws = AsyncMock()
        result = asyncio.run(svc.analyze_with_progress(reqs, websocket=ws))
        assert ws.send_json.called
        # Last call should be "complete" type
        last_call = ws.send_json.call_args_list[-1][0][0]
        assert last_call["type"] == "complete"

    def test_no_websocket(self, svc):
        reqs = [{"req_id": "REQ-001", "requirement": "Req.", "module": "M"}]
        svc._analyze_single_requirement_all_criteria = lambda r, rid, *a, **kw: {
            "req_id": rid, "score": "7/9", "characteristics": [], "evaluation": {}, "detailed_results": []
        }
        result = asyncio.run(svc.analyze_with_progress(reqs, websocket=None))
        assert "results" in result


# ---------------------------------------------------------------------------
# generate_suggestion_with_progress
# ---------------------------------------------------------------------------

class TestGenerateSuggestionWithProgress:
    def test_sends_complete_to_websocket(self, svc):
        reqs = [
            {"req_id": "REQ-001", "requirement": "Req.", "score": "5/9",
             "evaluation": {"Unambiguous": "vague"}, "module": None, "requirement_template": "Others"}
        ]
        fake = {
            "req_id": "REQ-001", "is_split": False, "suggested_requirement": "Fixed.",
            "split_requirements": None, "improvements": {}, "explanation": "", "success": True
        }
        svc._generate_suggestion_for_requirement = MagicMock(return_value=fake)
        ws = AsyncMock()
        result = asyncio.run(svc.generate_suggestion_with_progress(reqs, websocket=ws))
        assert ws.send_json.called
        last_call = ws.send_json.call_args_list[-1][0][0]
        assert last_call["type"] == "complete"

    def test_no_websocket(self, svc):
        reqs = [
            {"req_id": "REQ-001", "requirement": "Req.", "score": "9/9",
             "evaluation": {}, "module": None, "requirement_template": "Others"}
        ]
        result = asyncio.run(svc.generate_suggestion_with_progress(reqs, websocket=None))
        assert "results" in result
