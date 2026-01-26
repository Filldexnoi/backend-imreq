import os
from google import genai
from typing import Dict, List
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

class GeminiService:
    """
    Optimized Gemini Service with parallel processing
    """
    
    CRITERION_MEANING: Dict[str, str] = {
        "Appropriate": "The specific intent and amount of detail of the requirement is appropriate to the level of the entity to which it refers (level of abstraction appropriate to the level of entity). This includes avoiding unnecessary constraints on the architecture or design while allowing implementation independence to the extent possible.",
        "Complete": "The requirement sufficiently describes the necessary capability, characteristic, constraint or quality factor to meet the entity need without needing other information to understand the requirement.",
        "Conforming": "The individual items conform to an approved standard template and style for writing requirements, when applicable.",
        "Correct": "The requirement is an accurate representation of the entity need from which it was transformed.",
        "Feasible": "The requirement can be realized within system constraints (e.g., cost, schedule, technical) with acceptable risk.",
        "Necessary": "The requirement defines an essential capability, characteristic, constraint and/or quality factor. If it is not included in the set of requirements, a deficiency in capability or characteristic will exist, which cannot be fulfilled by implementing other requirements.",
        "Singular": "The requirement states a single capability, characteristic, constraint or quality factor.",
        "Unambiguous": "The requirement is stated in such a way so that it can be interpreted in only one way. The requirement is stated simply and is easy to understand.",
        "Verifiable": "The requirement is structured and worded such that its realization can be proven (verified) to the customer's satisfaction at the level the requirements exists. Verifiability is enhanced when the requirement is measurable.",
    }
    
    def __init__(self, max_workers: int = 10):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=api_key)
        self.model = 'gemini-2.0-flash-lite'
        self.max_workers = max_workers
        self.generation_config =  {
                "temperature": 0,
                "top_p": 1,
                "top_k": 1
        }
    
    def _analyze_single_requirement_all_criteria(self, requirement: str, req_id: str) -> Dict:
        """
        Analyze ONE requirement against ALL 9 criteria in ONE API call
        """
        criteria_text = "\n".join([
            f"{i+1}. {criterion}: {meaning}"
            for i, (criterion, meaning) in enumerate(self.CRITERION_MEANING.items())
        ])
        
        prompt = f"""Context: You're a software requirement expert.
        Analyze this requirement against ALL 9 ISO/IEC/IEEE 29148 quality criteria.

        Requirement ID: {req_id}
        Requirement: "{requirement}"

        ISO 29148 Quality Criteria:
        {criteria_text}

        Instructions:
        1) Evaluate ALL 9 criteria thoroughly
        2) Respond in Thai (software terms can use English)
        3) Return strict JSON:
        {{
        "req_id": "{req_id}",
        "results": [
            {{
            "criterion": "Appropriate",
            "pass": true|false,
            "score": 1|0,
            "reason": "<why it failed in Thai (empty if passed)>",
            "suggestion": "<how to fix in Thai (empty if passed)>"
            }},
            ... (all 9 criteria)
        ]
        }}

        For FAILED criteria: provide detailed reason and specific suggestion
        For PASSED criteria: leave reason and suggestion empty
        Be specific and reference the actual requirement text.
        Output: JSON only."""
        
        try:
            response = self.client.models.generate_content(
                model= self.model,
                contents=prompt,
                config= self.generation_config
            )
            
            result_text = response.text.strip()
            if not result_text:
                raise ValueError("LLM returned empty response")

            # Extract JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(result_text)
            
            # Process results
            passed_criteria = []
            failed_evaluation = {}
            total_score = 0
            
            for r in data['results']:
                criterion = r.get('criterion', '')
                is_passed = r.get('pass', False)
                
                if is_passed:
                    passed_criteria.append(criterion)
                    total_score += 1
                else:
                    # Store only reason (not suggestion) as string
                    reason = r.get('reason', '')
                    failed_evaluation[criterion] = reason if reason else "ไม่ผ่านเกณฑ์"
            
            return {
                "req_id": req_id,
                "score": f"{total_score}/9",
                "characteristics": passed_criteria,
                "evaluation": failed_evaluation,  # JSON object
                "detailed_results": data['results']
            }
        except Exception as e:
            return {
                "req_id": req_id,
                "score": "0/9",
                "characteristics": "",
                "evaluation": {"error": f"เกิดข้อผิดพลาด: {str(e)}"},
                "detailed_results": []
            }
    
    async def analyze_requirements_parallel(
        self, 
        requirements: List[Dict],
        progress_callback=None
    ) -> Dict:
        """
        Analyze requirements in parallel
        """
        total = len(requirements)
        results = []
        
        # Create async tasks
        loop = asyncio.get_event_loop()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            futures = [
                loop.run_in_executor(
                    executor,
                    self._analyze_single_requirement_all_criteria,
                    req['requirement'],
                    req['req_id']
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
                    progress_callback(completed, total)
        
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
        requirements: List[Dict]
    ) -> Dict:
        """
        Synchronous version for non-async contexts
        """
        return asyncio.run(self.analyze_requirements_parallel(requirements))
    
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
        websocket=None
    ):
        """
        Analyze with real-time progress updates via WebSocket
        """
        total = len(requirements)
        
        async def progress_callback(completed, total):
            if websocket:
                await websocket.send_json({
                    "type": "progress",
                    "completed": completed,
                    "total": total,
                    "percentage": (completed / total) * 100
                })
        
        result = await self.analyze_requirements_parallel(
            requirements,
            progress_callback=progress_callback
        )
        
        if websocket:
            await websocket.send_json({
                "type": "complete",
                "result": result
            })
        
        return result
    
    def _generate_suggestion_for_requirement(
        self, 
        req_id: str,
        requirement: str,
        evaluation: Dict[str, str],
        module: str = None
    ) -> Dict:
        """
        Generate improved requirement based on failed criteria
        """
        # Build context about failed criteria
        failed_criteria_text = "\n".join([
            f"- {criterion}: {reason}"
            for criterion, reason in evaluation.items()
            if criterion != 'error'
        ])
        
        # Build criteria definitions for context
        criteria_text = "\n".join([
            f"{i+1}. {criterion}: {meaning}"
            for i, (criterion, meaning) in enumerate(self.CRITERION_MEANING.items())
        ])
        
        prompt = f"""Context: You're a software requirement expert specializing in ISO/IEC/IEEE 29148 standards.

Task: Improve this requirement to pass ALL 9 quality criteria.

Requirement ID: {req_id}
Module: {module or 'N/A'}
Original Requirement: "{requirement}"

Failed Criteria and Reasons:
{failed_criteria_text}

ISO 29148 Quality Criteria Reference:
{criteria_text}

Instructions:
1) Rewrite the requirement to address ALL failed criteria
2) Keep the core intent and functionality of the original requirement
3) Make it specific, measurable, and unambiguous
4) Respond in Thai (technical terms can use English)
5) Return strict JSON format:

{{
  "req_id": "{req_id}",
  "suggested_requirement": "<improved requirement text in Thai>",
  "improvements": {{
    "criterion_name": "<explanation of what was fixed in Thai>",
    ...for each failed criterion
  }},
  "explanation": "<brief overall explanation of changes in Thai>"
}}

Focus on making the requirement:
- Clear and specific
- Measurable and verifiable
- Complete but not overly detailed
- Singular (one requirement per statement)
- Appropriate to the abstraction level

Output: JSON only, no preamble."""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=self.generation_config
            )
            
            result_text = response.text.strip()
            
            # Extract JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(result_text)
            
            return {
                "req_id": req_id,
                "suggested_requirement": data.get("suggested_requirement", ""),
                "improvements": data.get("improvements", {}),
                "explanation": data.get("explanation", ""),
                "success": True
            }
            
        except Exception as e:
            return {
                "req_id": req_id,
                "suggested_requirement": "",
                "improvements": {},
                "explanation": f"เกิดข้อผิดพลาด: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    async def generate_suggestions_parallel(
        self,
        analyzed_requirements: List[Dict],
        progress_callback=None
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
                    req.get('module')
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
                    progress_callback(completed, total)
        
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
        analyzed_requirements: List[Dict]
    ) -> Dict:
        """
        Synchronous version for non-async contexts
        """
        return asyncio.run(self.generate_suggestions_parallel(analyzed_requirements))
    
    async def generate_suggestion_with_progress(
        self,
        analyzed_requirements: List[Dict],
        websocket=None
    ):
        """
        Generate suggestions with real-time progress updates via WebSocket
        """
        async def progress_callback(completed, total):
            if websocket:
                await websocket.send_json({
                    "type": "progress",
                    "completed": completed,
                    "total": total,
                    "percentage": (completed / total) * 100
                })
        
        result = await self.generate_suggestions_parallel(
            analyzed_requirements,
            progress_callback=progress_callback
        )
        
        if websocket:
            await websocket.send_json({
                "type": "complete",
                "result": result
            })
        
        return result