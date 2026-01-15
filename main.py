from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import pandas as pd
import io
import json
import csv

from database import engine, get_db, Base
import models
import schemas
from routers import analyze

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ImReq API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to ImReq API with PostgreSQL"}

# Project endpoints
@app.get("/api/projects", response_model=List[schemas.Project])
def get_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = db.query(models.Project).offset(skip).limit(limit).all()
    return projects

@app.post("/api/projects", response_model=schemas.ResponseProjectCreate)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = models.Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

# Requirements endpoints
@app.get("/api/projects/{project_id}/originrequirements", response_model=List[schemas.OriginRequirement])
def get_origin_requirements(
    project_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    # Check if project exists
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    requirements = db.query(models.OriginRequirement)\
        .filter(models.OriginRequirement.project_id == project_id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return requirements

@app.post("/api/projects/{project_id}/originrequirements", response_model=schemas.ResponseOriginRequirementCreate)
async def create_origin_requirement(
    project_id: UUID,
    file: UploadFile = File(...),
    mapping: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        mapping_obj = schemas.ColumnMapping(**json.loads(mapping))
    except Exception as e:
        raise HTTPException(400, f"mapping ไม่ถูกต้อง: {e}")
    
    # Check if project exists
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))

    rows = []
    for row in reader:
        try:
            rows.append({
                "req_id": row[mapping_obj.req_id],
                "module": row[mapping_obj.module],
                "requirement": row[mapping_obj.requirement],
            })
        except KeyError as e:
            raise HTTPException(
                400,
                f"ไม่พบ column {e} ใน CSV"
            )

    objects = [
        models.OriginRequirement(
            project_id=project_id,
            **r
        ) for r in rows
    ]

    db.bulk_save_objects(objects)
    db.commit()
    return { "inserted_rows" : len(rows)}
    
@app.get("/api/projects/{project_id}/analyzedrequirements", response_model=List[schemas.AnalyzedRequirement])
def get_analyzed_requirements(
    project_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    # Check if project exists
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    requirements = db.query(models.AnalyzedRequirement)\
        .filter(models.AnalyzedRequirement.project_id == project_id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return requirements

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)