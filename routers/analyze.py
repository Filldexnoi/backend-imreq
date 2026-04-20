from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import asyncio
import logging

from database import get_db, SessionLocal, get_db_with_retry
import models
from services.gemini_service import GeminiService
from services.auth import get_current_active_user

router = APIRouter(prefix="/api/analyze-parallel", tags=["analyze-parallel"])

# Initialize with 10 parallel workers
gemini_service = GeminiService(max_workers=10)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_project_ownership(project_id: UUID, user_id: UUID, db: Session) -> models.Project:
    """Verify that project exists and belongs to user"""
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == user_id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project

@router.post("/projects/{project_id}/requirements")
async def analyze_project_requirements_parallel(
    project_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Parallel detailed analysis
    - Each requirement analyzed thoroughly (all 9 criteria)
    - Multiple requirements processed simultaneously
    - 10x-20x faster than sequential
    
    Performance:
    - 100 requirements = 100 API calls (detailed)
    - With 10 workers: ~30-60 seconds
    - Sequential would take: 5-10 minutes
    """

    # Verify project ownership
    project = verify_project_ownership(project_id, current_user.id, db)
    
    # Get origin requirements
    origin_requirements = db.query(models.OriginRequirement)\
        .filter(models.OriginRequirement.project_id == project_id)\
        .all()
    
    if not origin_requirements:
        raise HTTPException(status_code=404, detail="No origin requirements found")
    
    # Log the actual count
    logger.info(f"Found {len(origin_requirements)} origin requirements for project {project_id}")
    
    # Check for duplicate req_ids
    req_ids = [req.req_id for req in origin_requirements]
    unique_req_ids = set(req_ids)
    if len(req_ids) != len(unique_req_ids):
        logger.warning(f"Found duplicate req_ids! Total: {len(req_ids)}, Unique: {len(unique_req_ids)}")
        # Count duplicates
        from collections import Counter
        duplicates = {k: v for k, v in Counter(req_ids).items() if v > 1}
        logger.warning(f"Duplicate req_ids: {duplicates}")
    
    # Prepare data - Use unique requirements only based on req_id
    seen_req_ids = set()
    req_data = []
    for req in origin_requirements:
        if req.req_id not in seen_req_ids:
            req_data.append({
                "req_id": req.req_id,
                "module": req.module,
                "requirement": req.requirement
            })
            seen_req_ids.add(req.req_id)
        else:
            logger.warning(f"Skipping duplicate req_id: {req.req_id}")
    
    total_reqs = len(req_data)
    logger.info(f"Analyzing {total_reqs} unique requirements")
    
    # Snapshot data needed for LLM (plain values, no live ORM objects)
    requirement_template = project.requirement_template or "Others"
    reference_context = gemini_service._extract_reference_text(project.reference_files or [])
    origin_req_snapshot = [
        {"req_id": r.req_id, "module": r.module, "requirement": r.requirement}
        for r in origin_requirements
    ]

    # Release DB connection BEFORE the long LLM processing
    db.close()

    if reference_context:
        logger.info(f"Reference context extracted: {len(reference_context)} chars")
    else:
        logger.info("Reference context: none (Necessary/Feasible/Correct → CANNOT_DETERMINE)")
    logger.info(f"Using requirement template: {requirement_template}")

    try:
        # Parallel analysis — no DB connection held here
        result = await gemini_service.analyze_requirements_parallel(
            req_data,
            requirement_template,
            reference_context=reference_context,
        )
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # Open a fresh DB session just for saving results (retry if DB is in recovery)
    db_save = get_db_with_retry()
    try:
        deleted_count = db_save.query(models.AnalyzedRequirement)\
            .filter(models.AnalyzedRequirement.project_id == project_id)\
            .delete()
        logger.info(f"Deleted {deleted_count} old analyzed requirements")
        db_save.commit()

        analyzed_count = 0
        saved_req_ids = set()

        for analysis in result['results']:
            req_id = analysis['req_id']
            if req_id in saved_req_ids:
                logger.warning(f"Skipping duplicate analysis result for req_id: {req_id}")
                continue

            origin_req = next(
                (r for r in origin_req_snapshot if r["req_id"] == req_id), None
            )

            if origin_req:
                characteristics = analysis.get('characteristics', [])
                if isinstance(characteristics, str):
                    try:
                        import json
                        characteristics = json.loads(characteristics)
                    except Exception:
                        characteristics = []
                elif not isinstance(characteristics, list):
                    characteristics = []

                db_save.add(models.AnalyzedRequirement(
                    req_id=origin_req["req_id"],
                    project_id=project_id,
                    module=origin_req["module"],
                    requirement=origin_req["requirement"],
                    score=analysis.get('score', '0/9'),
                    characteristics=characteristics,
                    evaluation=analysis.get('evaluation', {}),
                ))
                saved_req_ids.add(req_id)
                analyzed_count += 1
            else:
                logger.warning(f"Origin requirement not found for req_id: {req_id}")

        db_save.commit()
        logger.info(f"Saved {analyzed_count} analyzed requirements")

        return {
            "message": "Parallel analysis completed",
            "method": "detailed_parallel",
            "analyzed_count": analyzed_count,
            "total_requirements": total_reqs,
            "origin_requirements_count": len(origin_req_snapshot),
            "unique_requirements_analyzed": len(saved_req_ids),
            "api_calls_used": total_reqs,
            "workers": gemini_service.max_workers,
            "summary": result.get('summary', {}),
            "performance": {
                "method": "parallel",
                "workers": gemini_service.max_workers,
                "detail_level": "complete (all 9 criteria per requirement)"
            }
        }
    except Exception as e:
        db_save.rollback()
        logger.error(f"Save failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Save failed: {str(e)}")
    finally:
        db_save.close()

@router.post("/projects/{project_id}/requirements/{req_id}")
async def analyze_single_requirement_detailed(
    project_id: UUID,
    req_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Analyze single requirement with full details
    1 API call, all 9 criteria with detailed justifications
    """
    # Get project to access requirement_template
    project = verify_project_ownership(project_id, current_user.id, db)

    origin_req = db.query(models.OriginRequirement)\
        .filter(models.OriginRequirement.project_id == project_id)\
        .filter(models.OriginRequirement.id == req_id)\
        .first()

    if not origin_req:
        raise HTTPException(status_code=404, detail="Requirement not found")

    try:
        # Get requirement template from project
        requirement_template = project.requirement_template or "Others"

        # Extract text from reference files for context-dependent criteria
        reference_context = gemini_service._extract_reference_text(project.reference_files or [])
        if reference_context:
            logger.info(f"[single] Reference context extracted: {len(reference_context)} chars | preview: {reference_context[:200]!r}")
        else:
            logger.info("[single] Reference context: none (Necessary/Feasible/Correct → CANNOT_DETERMINE)")

        # Detailed analysis
        result = gemini_service._analyze_single_requirement_all_criteria(
            origin_req.requirement,
            origin_req.req_id,
            requirement_template,
            reference_context=reference_context,
        )
        
        if result.get("evaluation", {}).get("error"):
            raise HTTPException(status_code=500, detail=f"Analysis failed: {result['evaluation']['error']}")
        
        # Check if already exists to prevent duplicates
        analyzed_req = db.query(models.AnalyzedRequirement)\
            .filter(models.AnalyzedRequirement.project_id == project_id)\
            .filter(models.AnalyzedRequirement.req_id == origin_req.req_id)\
            .first()
        
        characteristics = result.get('characteristics', [])
        
        # Ensure characteristics is a list (not a string)
        if isinstance(characteristics, str):
            try:
                import json
                characteristics = json.loads(characteristics)
            except:
                characteristics = []
        elif not isinstance(characteristics, list):
            characteristics = []
        
        if analyzed_req:
            # Update existing
            analyzed_req.score = result['score']
            analyzed_req.characteristics = characteristics
            analyzed_req.evaluation = result.get('evaluation', {})
            analyzed_req.requirement = origin_req.requirement
            analyzed_req.module = origin_req.module
            logger.info(f"Updated existing analyzed requirement: {origin_req.req_id}")
        else:
            # Create new
            analyzed_req = models.AnalyzedRequirement(
                req_id=origin_req.req_id,
                project_id=project_id,
                module=origin_req.module,
                requirement=origin_req.requirement,
                score=result['score'],
                characteristics=characteristics,
                evaluation=result.get('evaluation', {})
            )
            db.add(analyzed_req)
            logger.info(f"Created new analyzed requirement: {origin_req.req_id}")
        
        db.commit()
        db.refresh(analyzed_req)
        
        return {
            "req_id": analyzed_req.req_id,
            "score": analyzed_req.score,
            "characteristics": analyzed_req.characteristics,
            "evaluation": analyzed_req.evaluation,
            "detailed_results": result.get('detailed_results', []),
            "method": "detailed_single"
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Analysis failed for req_id {origin_req.req_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

async def _safe_send(websocket: WebSocket, data: dict) -> bool:
    """Send JSON on websocket, return False if connection is already closed."""
    try:
        await websocket.send_json(data)
        return True
    except Exception:
        return False


@router.websocket("/projects/{project_id}/requirements/ws")
async def analyze_with_progress(
    websocket: WebSocket,
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time progress updates
    """
    await websocket.accept()

    try:
        # Get project to access requirement_template
        project = db.query(models.Project).filter(
            models.Project.id == project_id
        ).first()

        if not project:
            await _safe_send(websocket, {"type": "error", "message": "Project not found"})
            return

        requirement_template = project.requirement_template or "Others"
        logger.info(f"WebSocket: Using requirement template: {requirement_template}")

        # Extract text from reference files for context-dependent criteria
        reference_context = gemini_service._extract_reference_text(project.reference_files or [])
        if reference_context:
            logger.info(f"WebSocket: Reference context extracted: {len(reference_context)} chars | preview: {reference_context[:200]!r}")
        else:
            logger.info("WebSocket: Reference context: none (Necessary/Feasible/Correct → CANNOT_DETERMINE)")

        # Get requirements
        origin_requirements = db.query(models.OriginRequirement)\
            .filter(models.OriginRequirement.project_id == project_id)\
            .all()

        if not origin_requirements:
            await _safe_send(websocket, {"type": "error", "message": "No requirements found"})
            return

        # Remove duplicates based on req_id
        seen_req_ids = set()
        req_data = []
        origin_req_snapshot = []
        for req in origin_requirements:
            if req.req_id not in seen_req_ids:
                req_data.append({
                    "req_id": req.req_id,
                    "module": req.module,
                    "requirement": req.requirement
                })
                origin_req_snapshot.append({
                    "req_id": req.req_id,
                    "module": req.module,
                    "requirement": req.requirement,
                })
                seen_req_ids.add(req.req_id)

        logger.info(f"WebSocket: Analyzing {len(req_data)} unique requirements")

        # Release DB connection BEFORE the long LLM processing
        db.close()

        # Send start message
        await _safe_send(websocket, {"type": "start", "total": len(req_data)})

        # Analyze with progress updates — no DB connection held here
        result = await gemini_service.analyze_with_progress(
            req_data,
            requirement_template,
            websocket=websocket,
            reference_context=reference_context,
        )

        # Open a fresh DB session just for saving results (retry if DB is in recovery)
        db_save = get_db_with_retry()
        try:
            deleted_count = db_save.query(models.AnalyzedRequirement)\
                .filter(models.AnalyzedRequirement.project_id == project_id)\
                .delete()
            logger.info(f"WebSocket: Deleted {deleted_count} old analyzed requirements")

            saved_req_ids = set()
            for analysis in result['results']:
                req_id = analysis['req_id']
                if req_id in saved_req_ids:
                    continue

                origin_req = next(
                    (r for r in origin_req_snapshot if r["req_id"] == req_id), None
                )

                if origin_req:
                    characteristics = analysis.get('characteristics', [])
                    if isinstance(characteristics, str):
                        try:
                            import json
                            characteristics = json.loads(characteristics)
                        except Exception:
                            characteristics = []
                    elif not isinstance(characteristics, list):
                        characteristics = []

                    db_save.add(models.AnalyzedRequirement(
                        req_id=origin_req["req_id"],
                        project_id=project_id,
                        module=origin_req["module"],
                        requirement=origin_req["requirement"],
                        score=analysis.get('score', '0/9'),
                        characteristics=characteristics,
                        evaluation=analysis.get('evaluation', {}),
                    ))
                    saved_req_ids.add(req_id)

            db_save.commit()
            logger.info(f"WebSocket: Saved {len(saved_req_ids)} analyzed requirements")
        except Exception as save_err:
            db_save.rollback()
            raise save_err
        finally:
            db_save.close()

        await _safe_send(websocket, {
            "type": "saved",
            "message": f"Saved {len(saved_req_ids)} analyzed requirements to database"
        })

    except WebSocketDisconnect:
        logger.info("WebSocket: Client disconnected")
    except Exception as e:
        msg = str(e)
        if "close frame" in msg or "ConnectionClosed" in type(e).__name__:
            logger.info("WebSocket: Connection closed by client")
        else:
            logger.error(f"WebSocket error: {msg}")
            await _safe_send(websocket, {"type": "error", "message": msg})
    finally:
        try:
            await websocket.close()
        except Exception:
            pass

# Debug endpoint to check database state
@router.get("/projects/{project_id}/requirements/debug")
async def debug_requirements(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Debug endpoint to check origin and analyzed requirements
    """
    origin_reqs = db.query(models.OriginRequirement)\
        .filter(models.OriginRequirement.project_id == project_id)\
        .all()
    
    analyzed_reqs = db.query(models.AnalyzedRequirement)\
        .filter(models.AnalyzedRequirement.project_id == project_id)\
        .all()
    
    # Count duplicates
    from collections import Counter
    origin_req_ids = [r.req_id for r in origin_reqs]
    analyzed_req_ids = [r.req_id for r in analyzed_reqs]
    
    origin_duplicates = {k: v for k, v in Counter(origin_req_ids).items() if v > 1}
    analyzed_duplicates = {k: v for k, v in Counter(analyzed_req_ids).items() if v > 1}
    
    return {
        "project_id": str(project_id),
        "origin_requirements": {
            "total": len(origin_reqs),
            "unique_req_ids": len(set(origin_req_ids)),
            "duplicates": origin_duplicates
        },
        "analyzed_requirements": {
            "total": len(analyzed_reqs),
            "unique_req_ids": len(set(analyzed_req_ids)),
            "duplicates": analyzed_duplicates
        }
    }

@router.get("/projects/{project_id}/reference-files/debug")
async def debug_reference_files(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Debug endpoint: แสดงเนื้อหาที่ extract จาก reference files ของ project
    ใช้ดูว่า Gemini จะได้รับข้อมูลอะไรจาก reference documents
    """
    project = db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    reference_files = project.reference_files or []

    # Show metadata of each file
    files_meta = [
        {
            "index": i,
            "name": f.get("name", ""),
            "type": f.get("type", ""),
            "size_bytes": f.get("size", 0),
            "has_content": bool(f.get("content")),
        }
        for i, f in enumerate(reference_files)
    ]

    # Extract text as Gemini would see it
    extracted_text = gemini_service._extract_reference_text(reference_files)

    return {
        "project_id": str(project_id),
        "total_files": len(reference_files),
        "files": files_meta,
        "extracted_text_length": len(extracted_text) if extracted_text else 0,
        "extracted_text": extracted_text or "(ไม่มีไฟล์ หรือ extract ไม่ได้)",
    }