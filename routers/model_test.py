"""
Blind model comparison test — NOT part of the main product flow.
Used internally to decide which LLM to adopt as the primary provider.

POST /api/model-test/run
  - Upload a CSV + column mapping + template
  - Analyzes + generates suggestions with both OpenAI and Gemini
  - Returns results labeled as model_a / model_b (randomly assigned)
  - Gemini is processed one requirement at a time to respect RPM limits
"""
import asyncio
import io
import json
import random
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

import logging

import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

router = APIRouter(prefix="/api/model-test", tags=["model-test"])
logger = logging.getLogger(__name__)

GEMINI_INTER_REQ_DELAY = 10.0  # Seconds to wait between Gemini requirement calls


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_csv(file_bytes: bytes, mapping: dict) -> List[Dict]:
    try:
        df = pd.read_csv(io.BytesIO(file_bytes))
    except Exception:
        df = pd.read_csv(io.BytesIO(file_bytes), encoding="latin-1")

    req_col = mapping.get("requirement", "")
    if not req_col or req_col not in df.columns:
        raise ValueError(f"Requirement column '{req_col}' not found in file")

    id_col = mapping.get("req_id") or None
    mod_col = mapping.get("module") or None

    reqs: List[Dict] = []
    for i, row in df.iterrows():
        req_text = str(row[req_col]).strip()
        if not req_text or req_text.lower() in ("nan", "none", ""):
            continue
        req_id = (
            str(row[id_col]).strip()
            if id_col and id_col in df.columns and str(row[id_col]).strip() not in ("nan", "none", "")
            else f"REQ{i + 1:03d}"
        )
        module = (
            str(row[mod_col]).strip()
            if mod_col and mod_col in df.columns and str(row[mod_col]).strip() not in ("nan", "none", "")
            else ""
        )
        reqs.append({"req_id": req_id, "requirement": req_text, "module": module})

    return reqs


def _attach_meta(analyzed_results: list, requirements: list, template: str) -> list:
    """Add requirement text, module, and template back onto analyzed dicts."""
    req_map = {r["req_id"]: r for r in requirements}
    out = []
    for a in analyzed_results:
        entry = dict(a)
        orig = req_map.get(a["req_id"], {})
        entry.setdefault("requirement", orig.get("requirement", ""))
        entry.setdefault("module", orig.get("module", ""))
        entry["requirement_template"] = template
        out.append(entry)
    return out


# ---------------------------------------------------------------------------
# Per-model runners (blocking — called from ThreadPoolExecutor)
# ---------------------------------------------------------------------------

def _run_openai(requirements: List[Dict], template: str) -> Dict:
    from services.llm_provider import OpenAIProvider
    from services.gemini_service import GeminiService

    total = len(requirements)
    logger.info(f"[OpenAI] Starting — {total} requirement(s), template={template}")

    service = GeminiService(llm_provider=OpenAIProvider())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        logger.info(f"[OpenAI] Analyzing all {total} requirements in parallel…")
        analysis = loop.run_until_complete(
            service.analyze_requirements_parallel(requirements, requirement_template=template)
        )
        logger.info(f"[OpenAI] Analysis done — avg score: {analysis.get('summary', {}).get('average_score', '?')}")

        flat = _attach_meta(analysis.get("results", []), requirements, template)
        needs = [r for r in flat if int((r.get("score") or "9/9").split("/")[0]) < 9]
        logger.info(f"[OpenAI] Generating suggestions for {len(needs)}/{total} requirement(s)…")
        suggestions = loop.run_until_complete(service.generate_suggestions_parallel(flat))
        logger.info(f"[OpenAI] Done — {suggestions.get('summary', {}).get('suggestions_generated', 0)} suggestion(s) generated")
    except Exception as e:
        logger.error(f"[OpenAI] Failed: {e}")
        return {"error": str(e), "analysis": {}, "suggestions": {}}
    finally:
        loop.close()

    return {"analysis": analysis, "suggestions": suggestions}


def _run_gemini(requirements: List[Dict], template: str, delay: float = GEMINI_INTER_REQ_DELAY) -> Dict:
    from services.llm_provider import GeminiProvider
    from services.gemini_service import GeminiService

    total = len(requirements)
    logger.info(f"[Gemini] Starting — {total} requirement(s), template={template}, delay={delay}s between each")

    service = GeminiService(llm_provider=GeminiProvider())

    all_analyzed: List[Dict] = []
    for i, req in enumerate(requirements):
        if i > 0:
            logger.info(f"[Gemini] Waiting {delay}s before next requirement (RPM limit)…")
            time.sleep(delay)
        logger.info(f"[Gemini] Analyzing [{i + 1}/{total}] req_id={req['req_id']}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            res = loop.run_until_complete(
                service.analyze_requirements_parallel([req], requirement_template=template)
            )
        except Exception as e:
            logger.error(f"[Gemini] Analysis failed for req_id={req['req_id']}: {e}")
            all_analyzed.append({
                "req_id": req["req_id"],
                "score": "0/9",
                "characteristics": [],
                "evaluation": {"error": str(e)},
                "detailed_results": [],
                "error": str(e),
            })
            continue
        finally:
            loop.close()
        score = res.get("results", [{}])[0].get("score", "?")
        logger.info(f"[Gemini] Done [{i + 1}/{total}] req_id={req['req_id']} — score={score}")
        all_analyzed.extend(res.get("results", []))

    logger.info(f"[Gemini] Analysis complete for all {total} requirement(s)")
    flat = _attach_meta(all_analyzed, requirements, template)

    sug_results: List[Dict] = []
    needs_sug = [r for r in flat if int((r.get("score") or "9/9").split("/")[0]) < 9]
    logger.info(f"[Gemini] Generating suggestions for {len(needs_sug)}/{total} requirement(s)…")

    sug_idx = 0
    for i, analyzed_req in enumerate(flat):
        score_str = analyzed_req.get("score", "9/9")
        try:
            current_score = int(score_str.split("/")[0])
        except Exception:
            current_score = 9
        if current_score >= 9:
            logger.info(f"[Gemini] Skipping suggestion for req_id={analyzed_req['req_id']} (score={score_str}, already perfect)")
            continue

        if sug_idx > 0:
            logger.info(f"[Gemini] Waiting {delay}s before next suggestion (RPM limit)…")
            time.sleep(delay)

        logger.info(f"[Gemini] Suggesting [{sug_idx + 1}/{len(needs_sug)}] req_id={analyzed_req['req_id']} (score={score_str})")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            res = loop.run_until_complete(service.generate_suggestions_parallel([analyzed_req]))
        except Exception as e:
            logger.error(f"[Gemini] Suggestion failed for req_id={analyzed_req['req_id']}: {e}")
            continue
        finally:
            loop.close()
        sug_results.extend(res.get("results", []))
        sug_idx += 1

    logger.info(f"[Gemini] All done — {len(sug_results)} suggestion(s) generated")

    total = len(all_analyzed)
    total_score = sum(
        int(r["score"].split("/")[0]) for r in all_analyzed if r.get("score") and "/" in r["score"]
    )
    avg = total_score / total if total else 0

    return {
        "analysis": {
            "results": all_analyzed,
            "summary": {
                "total_analyzed": total,
                "average_score": f"{avg:.1f}/9",
                "analysis_method": "sequential_per_requirement",
            },
        },
        "suggestions": {
            "results": sug_results,
            "summary": {"total_analyzed": total, "suggestions_generated": len(sug_results)},
        },
    }


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post("/run")
async def run_blind_test(
    file: UploadFile = File(...),
    mapping: str = Form(...),
    template: str = Form("ISO29148"),
):
    """
    Run analyze + suggest with both OpenAI and Gemini on the uploaded CSV.
    Results are returned as model_a / model_b with randomized assignment.
    Capped at 10 requirements to keep runtime manageable.
    """
    file_bytes = await file.read()

    try:
        mapping_dict = json.loads(mapping)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid mapping JSON")

    try:
        requirements = _parse_csv(file_bytes, mapping_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not requirements:
        raise HTTPException(status_code=400, detail="No requirements found in CSV")

    logger.info(f"[BlindTest] Starting with {len(requirements)} requirement(s), template={template}")
    logger.info(f"[BlindTest] OpenAI runs in parallel | Gemini runs sequentially with {GEMINI_INTER_REQ_DELAY}s delay")

    # Both models run concurrently in separate threads
    with ThreadPoolExecutor(max_workers=2) as pool:
        ev = asyncio.get_event_loop()
        openai_fut = ev.run_in_executor(pool, _run_openai, requirements, template)
        gemini_fut = ev.run_in_executor(pool, _run_gemini, requirements, template)
        openai_result, gemini_result = await asyncio.gather(openai_fut, gemini_fut)

    logger.info("[BlindTest] Both models finished — randomizing model assignment and requirement order")
    # Randomly assign model sides
    if random.random() < 0.5:
        model_a, model_b = openai_result, gemini_result
        reveal = {"model_a": "GPT (OpenAI)", "model_b": "Gemini (Google)"}
    else:
        model_a, model_b = gemini_result, openai_result
        reveal = {"model_a": "Gemini (Google)", "model_b": "GPT (OpenAI)"}

    # Shuffle requirement display order and randomize left/right side per requirement
    shuffled = [
        {
            "req_id": r["req_id"],
            "requirement": r["requirement"],
            "module": r.get("module", ""),
            "column_order": random.sample(["model_a", "model_b"], 2),
        }
        for r in requirements
    ]
    random.shuffle(shuffled)

    return {
        "model_a": model_a,
        "model_b": model_b,
        "total_requirements": len(requirements),
        "requirements": shuffled,
        "reveal": reveal,
    }
