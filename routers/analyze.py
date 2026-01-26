from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import asyncio
import logging

from database import get_db
import models
from services.gemini_service import GeminiService

router = APIRouter(prefix="/api/analyze-parallel", tags=["analyze-parallel"])

# Initialize with 10 parallel workers
gemini_service = GeminiService(max_workers=10)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/projects/{project_id}/requirements")
async def analyze_project_requirements_parallel(
    project_id: UUID,
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
    # Get project
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
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
    
    try:
        # Parallel analysis
        result = await gemini_service.analyze_requirements_parallel(req_data)
        
        # Clear existing analyzed requirements for this project
        deleted_count = db.query(models.AnalyzedRequirement)\
            .filter(models.AnalyzedRequirement.project_id == project_id)\
            .delete()
        logger.info(f"Deleted {deleted_count} old analyzed requirements")
        db.commit()
        
        # Save results - ensure no duplicates
        analyzed_count = 0
        saved_req_ids = set()
        
        for analysis in result['results']:
            req_id = analysis['req_id']
            
            # Skip if already saved
            if req_id in saved_req_ids:
                logger.warning(f"Skipping duplicate analysis result for req_id: {req_id}")
                continue
            
            # Find the origin requirement
            origin_req = next(
                (r for r in origin_requirements if r.req_id == req_id),
                None
            )
            
            if origin_req:
                characteristics = analysis.get('characteristics', [])
                
                # Ensure characteristics is a list (not a string)
                if isinstance(characteristics, str):
                    # If it's a string, try to parse it as JSON array
                    try:
                        import json
                        characteristics = json.loads(characteristics)
                    except:
                        # If parsing fails, split by comma or keep as empty list
                        characteristics = []
                elif not isinstance(characteristics, list):
                    characteristics = []
                
                analyzed_req = models.AnalyzedRequirement(
                    req_id=origin_req.req_id,
                    project_id=project_id,
                    module=origin_req.module,
                    requirement=origin_req.requirement,
                    score=analysis.get('score', '0/9'),
                    characteristics=characteristics,
                    evaluation=analysis.get('evaluation', {})
                )
                db.add(analyzed_req)
                saved_req_ids.add(req_id)
                analyzed_count += 1
            else:
                logger.warning(f"Origin requirement not found for req_id: {req_id}")
        
        db.commit()
        logger.info(f"Saved {analyzed_count} analyzed requirements")
        
        return {
            "message": "Parallel analysis completed",
            "method": "detailed_parallel",
            "analyzed_count": analyzed_count,
            "total_requirements": total_reqs,
            "origin_requirements_count": len(origin_requirements),
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
        db.rollback()
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/projects/{project_id}/requirements/{req_id}")
async def analyze_single_requirement_detailed(
    project_id: UUID,
    req_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Analyze single requirement with full details
    1 API call, all 9 criteria with detailed justifications
    """
    origin_req = db.query(models.OriginRequirement)\
        .filter(models.OriginRequirement.project_id == project_id)\
        .filter(models.OriginRequirement.id == req_id)\
        .first()
    
    if not origin_req:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    try:
        # Detailed analysis
        result = gemini_service._analyze_single_requirement_all_criteria(
            origin_req.requirement,
            origin_req.req_id
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
            analyzed_req.evaluation = result['evaluation']
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
                evaluation=result['evaluation']
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
        # Get requirements
        origin_requirements = db.query(models.OriginRequirement)\
            .filter(models.OriginRequirement.project_id == project_id)\
            .all()
        
        if not origin_requirements:
            await websocket.send_json({
                "type": "error",
                "message": "No requirements found"
            })
            await websocket.close()
            return
        
        # Remove duplicates based on req_id
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
        
        logger.info(f"WebSocket: Analyzing {len(req_data)} unique requirements")
        
        # Send start message
        await websocket.send_json({
            "type": "start",
            "total": len(req_data)
        })
        
        # Analyze with progress updates
        result = await gemini_service.analyze_with_progress(
            req_data,
            websocket=websocket
        )
        
        # Clear existing analyzed requirements
        deleted_count = db.query(models.AnalyzedRequirement)\
            .filter(models.AnalyzedRequirement.project_id == project_id)\
            .delete()
        logger.info(f"WebSocket: Deleted {deleted_count} old analyzed requirements")
        
        # Save results without duplicates
        saved_req_ids = set()
        for analysis in result['results']:
            req_id = analysis['req_id']
            
            if req_id in saved_req_ids:
                continue
            
            origin_req = next(
                (r for r in origin_requirements if r.req_id == req_id),
                None
            )
            
            if origin_req:
                characteristics = analysis.get('characteristics', [])
                
                # Ensure characteristics is a list (not a string)
                if isinstance(characteristics, str):
                    # If it's a string, try to parse it as JSON array
                    try:
                        import json
                        characteristics = json.loads(characteristics)
                    except:
                        # If parsing fails, keep as empty list
                        characteristics = []
                elif not isinstance(characteristics, list):
                    characteristics = []
                
                analyzed_req = models.AnalyzedRequirement(
                    req_id=origin_req.req_id,
                    project_id=project_id,
                    module=origin_req.module,
                    requirement=origin_req.requirement,
                    score=analysis.get('score', '0/9'),
                    characteristics=characteristics,
                    evaluation=analysis.get('evaluation', {})
                )
                db.add(analyzed_req)
                saved_req_ids.add(req_id)
        
        db.commit()
        logger.info(f"WebSocket: Saved {len(saved_req_ids)} analyzed requirements")
        
        await websocket.send_json({
            "type": "saved",
            "message": f"Saved {len(saved_req_ids)} analyzed requirements to database"
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