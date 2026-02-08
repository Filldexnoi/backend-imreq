from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List 
from uuid import UUID
import pandas as pd
import io
import json
import csv
import uuid

from database import engine, get_db, Base
import models
import schemas
from routers import analyze , suggestion  , export , auth
from services.auth import get_current_active_user

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ImReq API", version="1.0.0")

# Configure security scheme for Swagger UI
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.models import SecurityScheme
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="ImReq API",
        version="1.0.0",
        description="Requirements Analysis API with JWT Authentication",
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token from /api/auth/login"
        }
    }
    
    # Apply security to all endpoints except auth
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if not path.startswith("/api/auth"):
                openapi_schema["paths"][path][method]["security"] = [
                    {"BearerAuth": []}
                ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)
app.include_router(suggestion.router)
app.include_router(export.router)
app.include_router(auth.router)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to ImReq API with PostgreSQL"}

# Project endpoints
@app.get("/api/projects", response_model=List[schemas.Project])
def get_projects(skip: int = 0, limit: int = 100, current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    projects = db.query(models.Project)\
        .filter(models.Project.user_id == current_user.id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return projects

@app.get("/api/projects/{project_id}", response_model=schemas.Project)
def get_project_by_id(project_id: UUID, current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    project = db.query(models.Project)\
        .filter(
            models.Project.user_id == current_user.id,
            models.Project.id == project_id
            )\
        .first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.post("/api/projects", response_model=schemas.ResponseProjectCreate)
async def create_project(
    title: str = Form(...),
    description: str = Form(...),
    requirement_template: str = Form("Others"),
    files: List[UploadFile] = File(None),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Handle file uploads - store as base64 in database
    reference_files = []
    if files:
        import base64
        
        for file in files:
            # Read file content
            content = await file.read()
            
            # Convert to base64
            content_base64 = base64.b64encode(content).decode('utf-8')
            
            # Store file metadata with base64 content
            reference_files.append({
                "name": file.filename,
                "content": content_base64,
                "size": len(content),
                "type": file.content_type or "application/octet-stream"
            })
    
    # Create project
    db_project = models.Project(
        user_id=current_user.id,
        title=title,
        description=description,
        requirement_template=requirement_template,
        reference_files=reference_files if reference_files else None
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.put("/api/projects/{project_id}", response_model=schemas.Project)
async def update_project_by_id(
    project_id: UUID,
    title: str = Form(None),
    description: str = Form(None),
    requirement_template: str = Form(None),
    files: List[UploadFile] = File(None),
    current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):

    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    model_update = {}
    print(title,description)
    if title:
        model_update[models.Project.title] = title
    if description:
        model_update[models.Project.description] = description
    if requirement_template:
        model_update[models.Project.requirement_template] = requirement_template
    if files:
        import base64
        
        reference_files = []
        for file in files:
            # Read file content
            content = await file.read()
            
            # Convert to base64
            content_base64 = base64.b64encode(content).decode('utf-8')
            
            # Store file metadata with base64 content
            reference_files.append({
                "name": file.filename,
                "content": content_base64,
                "size": len(content),
                "type": file.content_type or "application/octet-stream"
            })
        
        model_update[models.Project.reference_files] = reference_files

    updated_rows = (
    db.query(models.Project)
    .filter(
        models.Project.user_id == current_user.id ,
        models.Project.id == project.id)
    .update(
            model_update,
            synchronize_session=False
        )
    )
    
    if updated_rows > 1:
        raise HTTPException(status_code=409, detail="Project updated failed because update more than 1") 
    db.commit()

    updated_project = db.query(models.Project).filter(
        models.Project.id == project.id,
        models.Project.user_id == current_user.id
    ).first()

    return updated_project

@app.delete("/api/projects/{project_id}", response_model=schemas.ResponseProjectCreate)
def delete_project_by_id(project_id: UUID,current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):

    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    origin_req = db.query(models.OriginRequirement).filter(
        models.OriginRequirement.project_id == project_id
    ).first()

    if origin_req:
        db.query(models.OriginRequirement)\
        .filter(
            models.OriginRequirement.project_id == project.id)\
        .delete(synchronize_session=False)
    
    analyze_req = db.query(models.AnalyzedRequirement).filter(
         models.AnalyzedRequirement.project_id == project_id
    ).first()

    if analyze_req:
        db.query(models.AnalyzedRequirement)\
        .filter(
            models.AnalyzedRequirement.project_id == project.id)\
        .delete(synchronize_session=False)

    suggest_req = db.query(models.SuggestedRequirement).filter(
         models.SuggestedRequirement.project_id == project_id
    ).first()

    if suggest_req:
        db.query(models.SuggestedRequirement)\
        .filter(
            models.SuggestedRequirement.project_id == project.id)\
        .delete(synchronize_session=False)
    
    select_req = db.query(models.SelectedRequirement).filter(
         models.SelectedRequirement.project_id == project_id
    ).first()

    if select_req:
        db.query(models.SelectedRequirement)\
        .filter(
            models.SelectedRequirement.project_id == project.id)\
        .delete(synchronize_session=False)


    deleted_rows = db.query(models.Project)\
        .filter(
            models.Project.user_id == current_user.id,
            models.Project.id == project.id)\
        .delete(synchronize_session=False)
    
    if deleted_rows > 1:
        raise HTTPException(status_code=409, detail="delete row more than 1")
    
    if deleted_rows == 0:
        raise HTTPException(status_code=409, detail="not delete anything")
    
    db.commit()

    return models.Project(id=project_id)

@app.get("/api/projects/{project_id}/reference-files/{file_index}")
async def download_reference_file(
    project_id: UUID,
    file_index: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Download a reference file by index"""
    from fastapi.responses import Response
    import base64
    
    # Get project
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if reference files exist
    if not project.reference_files or file_index >= len(project.reference_files):
        raise HTTPException(status_code=404, detail="Reference file not found")
    
    # Get file data
    file_data = project.reference_files[file_index]
    
    # Decode base64 content
    content = base64.b64decode(file_data['content'])
    
    # Return file
    return Response(
        content=content,
        media_type=file_data['type'],
        headers={
            'Content-Disposition': f'attachment; filename="{file_data["name"]}"'
        }
    )

# Requirements endpoints
@app.get("/api/projects/{project_id}/originrequirements", response_model=List[schemas.OriginRequirement])
def get_origin_requirements(
    project_id: UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if project exists
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()

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
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        mapping_obj = schemas.ColumnMapping(**json.loads(mapping))
    except Exception as e:
        raise HTTPException(400, f"mapping ไม่ถูกต้อง: {e}")
    
    # Check if project exists
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))

    rows = []
    row_number = 1

    for row in reader:
        try:
            # Requirement is required
            requirement_text = row.get(mapping_obj.requirement)
            if not requirement_text:
                raise HTTPException(400, f"Row {row_number}: requirement column '{mapping_obj.requirement}' is empty")
            
            # req_id: use from CSV if provided, otherwise auto-generate
            if mapping_obj.req_id and mapping_obj.req_id in row and row[mapping_obj.req_id]:
                req_id = row[mapping_obj.req_id]
            else:
                req_id = f"REQ-{row_number}"
            
            # module: use from CSV if provided, otherwise empty string
            if mapping_obj.module and mapping_obj.module in row:
                module = row[mapping_obj.module] or ""
            else:
                module = ""
            
            rows.append({
                "req_id": req_id,
                "module": module,
                "requirement": requirement_text,
            })
            row_number += 1

        except KeyError as e:
            raise HTTPException(
                400,
                f"Row {row_number}: ไม่พบ column {e} ใน CSV"
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
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if project exists
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    requirements = db.query(models.AnalyzedRequirement)\
        .filter(models.AnalyzedRequirement.project_id == project_id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return requirements

@app.get("/api/projects/{project_id}/suggestedrequirements",response_model=List[schemas.SuggestedRequirement])
def get_suggestions_for_project(
    project_id: UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all suggestions for a project
    """
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    suggestions = db.query(models.SuggestedRequirement)\
        .filter(models.SuggestedRequirement.project_id == project_id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return suggestions

@app.post("/api/projects/{project_id}/selectedrequirements")
def create_selected_requirements(
    project_id: UUID,
    selected_requirements: List[schemas.SelectedRequirementBase],
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 1. check project exists
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    num_selected = db.query(models.SelectedRequirement)\
        .filter(models.SelectedRequirement.project_id == project_id)\
        .count()
    
    if num_selected > 0:
        db.query(models.SelectedRequirement)\
        .filter(models.SelectedRequirement.project_id == project_id)\
        .delete(synchronize_session=False)

    # 2. build objects + inject project_id
    objects = [
        models.SelectedRequirement(
            project_id=project_id,
            **req.dict()
        )
        for req in selected_requirements
    ]

    # 3. bulk insert (performance friendly)
    db.bulk_save_objects(objects)
    db.commit()

    return {"inserted": len(objects)}

@app.get("/api/projects/{project_id}/selectedrequirements")
def get_selected_for_project(
    project_id: UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all suggestions for a project
    """
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    selecteds = db.query(models.SelectedRequirement)\
        .filter(models.SelectedRequirement.project_id == project_id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return selecteds
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)