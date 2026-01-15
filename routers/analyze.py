from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import asyncio

from database import get_db
import models
from services.gemini_service import GeminiService

router = APIRouter(prefix="/api/analyze-parallel", tags=["analyze-parallel"])

# Initialize with 10 parallel workers
gemini_service = GeminiService(max_workers=10)

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
    
    # Prepare data
    req_data = [
        {
            "req_id": req.req_id,
            "module": req.module,
            "requirement": req.requirement
        }
        for req in origin_requirements
    ]
    
    total_reqs = len(req_data)
    
    try:
        # Parallel analysis
        result = await gemini_service.analyze_requirements_parallel(req_data)
        
        # Clear existing analyzed requirements
        db.query(models.AnalyzedRequirement)\
            .filter(models.AnalyzedRequirement.project_id == project_id)\
            .delete()
        db.commit()
        
        # Save results
        analyzed_count = 0
        for analysis in result['results']:
            origin_req = next(
                (r for r in origin_requirements if r.req_id == analysis['req_id']),
                None
            )
            
            if origin_req:
                characteristics = analysis.get('characteristics', [])
                analyzed_req = models.AnalyzedRequirement(
                    req_id=origin_req.req_id,
                    project_id=project_id,
                    module=origin_req.module,
                    requirement=origin_req.requirement,
                    score=analysis.get('score', '0/9'),
                    characteristics=characteristics,
                    evaluation=analysis.get('evaluation', '')
                )
                db.add(analyzed_req)
                analyzed_count += 1
        
        db.commit()
        
        return {
            "message": "Parallel analysis completed",
            "method": "detailed_parallel",
            "analyzed_count": analyzed_count,
            "total_requirements": total_reqs,
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
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=f"Analysis failed: {result.get("error")}")
        # Save or update
        analyzed_req = db.query(models.AnalyzedRequirement)\
            .filter(models.AnalyzedRequirement.project_id == project_id)\
            .filter(models.AnalyzedRequirement.id == req_id)\
            .first()
        
        characteristics = result.get('characteristics', [])
        
        if analyzed_req:
            analyzed_req.score = result['score']
            analyzed_req.characteristics = characteristics
            analyzed_req.evaluation = result['evaluation']
        else:
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
        
        req_data = [
            {
                "req_id": req.req_id,
                "module": req.module,
                "requirement": req.requirement
            }
            for req in origin_requirements
        ]
        
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
        
        # Save results to database
        db.query(models.AnalyzedRequirement)\
            .filter(models.AnalyzedRequirement.project_id == project_id)\
            .delete()
        
        for analysis in result['results']:
            origin_req = next(
                (r for r in origin_requirements if r.req_id == analysis['req_id']),
                None
            )
            
            if origin_req:
                analyzed_req = models.AnalyzedRequirement(
                    req_id=origin_req.req_id,
                    project_id=project_id,
                    module=origin_req.module,
                    requirement=origin_req.requirement,
                    score=analysis.get('score', '0/9'),
                    characteristics=", ".join(analysis.get('characteristics', [])),
                    evaluation=analysis.get('evaluation', '')
                )
                db.add(analyzed_req)
        
        db.commit()
        
        await websocket.send_json({
            "type": "saved",
            "message": "Results saved to database"
        })
        
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        await websocket.close()