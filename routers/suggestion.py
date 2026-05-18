from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import asyncio
import logging
import os

from database import get_db, get_db_with_retry
import models
from services.gemini_service import GeminiService
from services.auth import get_current_active_user

router = APIRouter(prefix="/api/suggestions", tags=["suggestions"])

# Initialize suggestion service
suggestion_service = GeminiService(max_workers=10)

# Defaults from env (can still be overridden per-request via query params)
_DEFAULT_MIN_SIMILARITY = float(os.getenv("MIN_SIMILARITY", "0.5"))
_DEFAULT_MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

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

def filter_improvements_by_evaluation(
    improvements: dict, 
    evaluation: dict
) -> dict:
    """
    Filter improvements to only include criteria that actually failed.
    Only keep improvements for criteria present in evaluation (failed criteria).
    """
    if not evaluation or not improvements:
        return {}
    
    failed_criteria = set(evaluation.keys())
    return {
        criterion: improvement 
        for criterion, improvement in improvements.items() 
        if criterion in failed_criteria and criterion != 'error'
    }

@router.post("/projects/{project_id}/generate")
async def generate_suggestions_for_project(
    project_id: UUID,
    min_similarity: float = Query(default=_DEFAULT_MIN_SIMILARITY, ge=0.0, le=1.0),
    max_retries: int = Query(default=_DEFAULT_MAX_RETRIES, ge=1, le=5),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate improvement suggestions for all requirements in a project
    - Only processes requirements with score < 9/9
    - Requirements with 9/9 score are skipped
    - Runs in parallel for better performance
    """
    # Get project
    project = verify_project_ownership(project_id, current_user.id, db)
    
    # Get analyzed requirements
    analyzed_requirements = db.query(models.AnalyzedRequirement)\
        .filter(models.AnalyzedRequirement.project_id == project_id)\
        .all()
    
    if not analyzed_requirements:
        raise HTTPException(
            status_code=404, 
            detail="No analyzed requirements found. Please analyze requirements first."
        )
    
    # Prepare data
    req_data = []
    for req in analyzed_requirements:
        req_data.append({
            "req_id": req.req_id,
            "module": req.module,
            "requirement": req.requirement,
            "score": req.score,
            "evaluation": req.evaluation or {},
            "requirement_template": project.requirement_template or "Others"
        })
    
    logger.info(f"Found {len(req_data)} analyzed requirements for project {project_id}")
    
    try:
        # Generate suggestions in parallel
        result = await suggestion_service.generate_suggestions_parallel(
            req_data,
            min_similarity=min_similarity,
            max_retries=max_retries,
        )
        
        # Clear existing suggestions for this project
        deleted_count = db.query(models.SuggestedRequirement)\
            .filter(models.SuggestedRequirement.project_id == project_id)\
            .delete()
        logger.info(f"Deleted {deleted_count} old suggestions")
        db.commit()
        
        # Save new suggestions
        saved_count = 0
        for suggestion in result['results']:
            if not suggestion.get('success', False):
                logger.warning(f"Failed to generate suggestion for {suggestion['req_id']}")
                continue
            
            # Find the original analyzed requirement
            analyzed_req = next(
                (r for r in analyzed_requirements if r.req_id == suggestion['req_id']),
                None
            )
            
            if analyzed_req:
                # Filter improvements to only failed criteria
                filtered_improvements = filter_improvements_by_evaluation(
                    suggestion.get('improvements', {}),
                    analyzed_req.evaluation or {}
                )
                
                suggested_req = models.SuggestedRequirement(
                    req_id=analyzed_req.req_id,
                    project_id=project_id,
                    module=analyzed_req.module,
                    original_requirement=analyzed_req.requirement,
                    suggested_requirement=suggestion.get('suggested_requirement'),
                    original_score=analyzed_req.score,
                    improvements=filtered_improvements,
                    is_split=suggestion.get('is_split', False),
                    split_requirements=suggestion.get('split_requirements')
                )
                db.add(suggested_req)
                saved_count += 1
        
        db.commit()
        logger.info(f"Saved {saved_count} suggestions")
        
        return {
            "message": "Suggestions generated successfully",
            "saved_count": saved_count,
            "summary": result.get('summary', {}),
            "performance": {
                "method": "parallel",
                "workers": suggestion_service.max_workers
            }
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Suggestion generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Suggestion generation failed: {str(e)}")

@router.post("/projects/{project_id}/requirements/{req_id}/generate")
async def generate_suggestion_for_single_requirement(
    project_id: UUID,
    req_id: str,
    min_similarity: float = Query(default=_DEFAULT_MIN_SIMILARITY, ge=0.0, le=1.0),
    max_retries: int = Query(default=_DEFAULT_MAX_RETRIES, ge=1, le=5),
    db: Session = Depends(get_db)
):
    """
    Generate improvement suggestion for a single requirement
    Returns 400 if requirement already has 9/9 score
    """
    # Get project to get requirement_template
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Find analyzed requirement by req_id (not UUID id)
    analyzed_req = db.query(models.AnalyzedRequirement)\
        .filter(models.AnalyzedRequirement.project_id == project_id)\
        .filter(models.AnalyzedRequirement.req_id == req_id)\
        .first()

    if not analyzed_req:
        raise HTTPException(
            status_code=404,
            detail="Analyzed requirement not found. Please analyze this requirement first."
        )

    # Check if already perfect
    score = analyzed_req.score or "0/9"
    current_score = int(score.split('/')[0])

    if current_score >= 9:
        return {
            "message": "Requirement already passes all 9 criteria",
            "req_id": req_id,
            "score": score,
            "suggestion_needed": False
        }

    try:
        # Generate suggestion
        result = suggestion_service._generate_suggestion_for_requirement(
            req_id=analyzed_req.req_id,
            requirement=analyzed_req.requirement,
            evaluation=analyzed_req.evaluation or {},
            module=analyzed_req.module,
            requirement_template=project.requirement_template or "Others",
            min_similarity=min_similarity,
            max_retries=max_retries,
        )
        
        if not result.get('success', False):
            raise HTTPException(
                status_code=500, 
                detail=f"Suggestion generation failed: {result.get('error', 'Unknown error')}"
            )
        
        # Save or update suggestion
        existing_suggestion = db.query(models.SuggestedRequirement)\
            .filter(models.SuggestedRequirement.project_id == project_id)\
            .filter(models.SuggestedRequirement.req_id == req_id)\
            .first()
        
        if existing_suggestion:
            # Update existing
            existing_suggestion.original_requirement = analyzed_req.requirement
            existing_suggestion.suggested_requirement = result.get('suggested_requirement')
            existing_suggestion.original_score = analyzed_req.score
            existing_suggestion.improvements = result.get('improvements', {})
            existing_suggestion.module = analyzed_req.module
            existing_suggestion.is_split = result.get('is_split', False)
            existing_suggestion.split_requirements = result.get('split_requirements')
            logger.info(f"Updated existing suggestion for {req_id}")
        else:
            # Create new
            new_suggestion = models.SuggestedRequirement(
                req_id=analyzed_req.req_id,
                project_id=project_id,
                module=analyzed_req.module,
                original_requirement=analyzed_req.requirement,
                suggested_requirement=result.get('suggested_requirement'),
                original_score=analyzed_req.score,
                improvements=result.get('improvements', {}),
                is_split=result.get('is_split', False),
                split_requirements=result.get('split_requirements')
            )
            db.add(new_suggestion)
            logger.info(f"Created new suggestion for {req_id}")

        db.commit()

        return {
            "req_id": req_id,
            "original_requirement": analyzed_req.requirement,
            "is_split": result.get('is_split', False),
            "suggested_requirement": result.get('suggested_requirement'),
            "split_requirements": result.get('split_requirements'),
            "original_score": analyzed_req.score,
            "improvements": result.get('improvements', {}),
            "explanation": result.get('explanation', ''),
            "message": "Suggestion generated successfully"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Suggestion generation failed for {req_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Suggestion generation failed: {str(e)}")

@router.get("/projects/{project_id}")
async def get_suggestions_for_project(
    project_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all suggestions for a project
    """
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    suggestions = db.query(models.SuggestedRequirement)\
        .filter(models.SuggestedRequirement.project_id == project_id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return {
        "project_id": str(project_id),
        "total": len(suggestions),
        "suggestions": [
            {
                "id": str(s.id),
                "req_id": s.req_id,
                "module": s.module,
                "original_requirement": s.original_requirement,
                "suggested_requirement": s.suggested_requirement,
                "original_score": s.original_score,
                "improvements": s.improvements,
                "created_at": s.created_at.isoformat() if s.created_at else None
            }
            for s in suggestions
        ]
    }

@router.get("/projects/{project_id}/requirements/{req_id}")
async def get_suggestion_for_requirement(
    project_id: UUID,
    req_id: str,
    db: Session = Depends(get_db)
):
    """
    Get suggestion for a specific requirement
    """
    suggestion = db.query(models.SuggestedRequirement)\
        .filter(models.SuggestedRequirement.project_id == project_id)\
        .filter(models.SuggestedRequirement.req_id == req_id)\
        .first()
    
    if not suggestion:
        raise HTTPException(
            status_code=404, 
            detail="Suggestion not found. Please generate suggestions first."
        )
    
    return {
        "id": str(suggestion.id),
        "req_id": suggestion.req_id,
        "module": suggestion.module,
        "original_requirement": suggestion.original_requirement,
        "suggested_requirement": suggestion.suggested_requirement,
        "original_score": suggestion.original_score,
        "improvements": suggestion.improvements,
        "created_at": suggestion.created_at.isoformat() if suggestion.created_at else None
    }

@router.websocket("/projects/{project_id}/generate/ws")
async def generate_suggestions_with_progress(
    websocket: WebSocket,
    project_id: UUID,
    min_similarity: float = Query(default=_DEFAULT_MIN_SIMILARITY, ge=0.0, le=1.0),
    max_retries: int = Query(default=_DEFAULT_MAX_RETRIES, ge=1, le=5),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time progress updates during suggestion generation
    """
    await websocket.accept()
    
    try:
        # Get project to get requirement_template
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            await websocket.send_json({
                "type": "error",
                "message": "Project not found"
            })
            await websocket.close()
            return

        # Get analyzed requirements
        analyzed_requirements = db.query(models.AnalyzedRequirement)\
            .filter(models.AnalyzedRequirement.project_id == project_id)\
            .all()

        if not analyzed_requirements:
            await websocket.send_json({
                "type": "error",
                "message": "No analyzed requirements found"
            })
            await websocket.close()
            return

        req_data = [
            {
                "req_id": req.req_id,
                "module": req.module,
                "requirement": req.requirement,
                "score": req.score,
                "evaluation": req.evaluation or {},
                "requirement_template": project.requirement_template or "Others"
            }
            for req in analyzed_requirements
        ]
        # Snapshot evaluations for filtering later (plain dicts, no live ORM)
        eval_snapshot = {req.req_id: req.evaluation or {} for req in analyzed_requirements}
        analyzed_snapshot = [
            {"req_id": r.req_id, "module": r.module, "requirement": r.requirement, "score": r.score}
            for r in analyzed_requirements
        ]

        # Release DB connection BEFORE the long LLM processing
        db.close()

        # Send start message
        await websocket.send_json({
            "type": "start",
            "total": len(req_data)
        })

        # Generate suggestions with progress — no DB connection held here
        result = await suggestion_service.generate_suggestion_with_progress(
            req_data,
            websocket=websocket,
            min_similarity=min_similarity,
            max_retries=max_retries,
        )

        # Open a fresh DB session just for saving results (retry if DB is in recovery)
        db_save = get_db_with_retry()
        try:
            db_save.query(models.SuggestedRequirement)\
                .filter(models.SuggestedRequirement.project_id == project_id)\
                .delete()

            saved_count = 0
            for suggestion in result['results']:
                if not suggestion.get('success', False):
                    continue

                analyzed_req = next(
                    (r for r in analyzed_snapshot if r["req_id"] == suggestion['req_id']),
                    None
                )

                if analyzed_req:
                    filtered_improvements = filter_improvements_by_evaluation(
                        suggestion.get('improvements', {}),
                        eval_snapshot.get(analyzed_req["req_id"], {})
                    )

                    db_save.add(models.SuggestedRequirement(
                        req_id=analyzed_req["req_id"],
                        project_id=project_id,
                        module=analyzed_req["module"],
                        original_requirement=analyzed_req["requirement"],
                        suggested_requirement=suggestion.get('suggested_requirement'),
                        original_score=analyzed_req["score"],
                        improvements=filtered_improvements,
                        is_split=suggestion.get('is_split', False),
                        split_requirements=suggestion.get('split_requirements'),
                    ))
                    saved_count += 1

            db_save.commit()
        except Exception as save_err:
            db_save.rollback()
            raise save_err
        finally:
            db_save.close()

        await websocket.send_json({
            "type": "saved",
            "message": f"Saved {saved_count} suggestions to database",
            "saved_count": saved_count
        })
        
    except WebSocketDisconnect:
        logger.info("WebSocket: Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        await websocket.close()

@router.delete("/projects/{project_id}")
async def delete_suggestions_for_project(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete all suggestions for a project
    """
    deleted_count = db.query(models.SuggestedRequirement)\
        .filter(models.SuggestedRequirement.project_id == project_id)\
        .delete()
    
    db.commit()
    
    return {
        "message": f"Deleted {deleted_count} suggestions",
        "deleted_count": deleted_count
    }