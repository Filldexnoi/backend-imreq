from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import asyncio
import logging

from database import get_db
import models
from services.gemini_service import GeminiService
from services.auth import get_current_active_user

router = APIRouter(prefix="/api/suggestions", tags=["suggestions"])

# Initialize suggestion service
suggestion_service = GeminiService(max_workers=10)

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
            "evaluation": req.evaluation or {}
        })
    
    logger.info(f"Found {len(req_data)} analyzed requirements for project {project_id}")
    
    try:
        # Generate suggestions in parallel
        result = await suggestion_service.generate_suggestions_parallel(req_data)
        
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
                    suggested_requirement=suggestion.get('suggested_requirement', ''),
                    original_score=analyzed_req.score,
                    improvements=filtered_improvements
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
    db: Session = Depends(get_db)
):
    """
    Generate improvement suggestion for a single requirement
    Returns 400 if requirement already has 9/9 score
    """
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
            module=analyzed_req.module
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
            existing_suggestion.suggested_requirement = result.get('suggested_requirement', '')
            existing_suggestion.original_score = analyzed_req.score
            existing_suggestion.improvements = result.get('improvements', {})
            existing_suggestion.module = analyzed_req.module
            logger.info(f"Updated existing suggestion for {req_id}")
        else:
            # Create new
            new_suggestion = models.SuggestedRequirement(
                req_id=analyzed_req.req_id,
                project_id=project_id,
                module=analyzed_req.module,
                original_requirement=analyzed_req.requirement,
                suggested_requirement=result.get('suggested_requirement', ''),
                original_score=analyzed_req.score,
                improvements=result.get('improvements', {})
            )
            db.add(new_suggestion)
            logger.info(f"Created new suggestion for {req_id}")
        
        db.commit()
        
        return {
            "req_id": req_id,
            "original_requirement": analyzed_req.requirement,
            "suggested_requirement": result.get('suggested_requirement', ''),
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
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time progress updates during suggestion generation
    """
    await websocket.accept()
    
    try:
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
                "evaluation": req.evaluation or {}
            }
            for req in analyzed_requirements
        ]
        
        # Send start message
        await websocket.send_json({
            "type": "start",
            "total": len(req_data)
        })
        
        # Generate suggestions with progress
        result = await suggestion_service.generate_suggestion_with_progress(
            req_data,
            websocket=websocket
        )
        
        # Clear old suggestions
        db.query(models.SuggestedRequirement)\
            .filter(models.SuggestedRequirement.project_id == project_id)\
            .delete()
        
        # Save results
        saved_count = 0
        for suggestion in result['results']:
            if not suggestion.get('success', False):
                continue
            
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
                    suggested_requirement=suggestion.get('suggested_requirement', ''),
                    original_score=analyzed_req.score,
                    improvements=filtered_improvements
                )
                db.add(suggested_req)
                saved_count += 1
        
        db.commit()
        
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