import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import asc
from typing import List
from uuid import UUID
import pandas as pd
import io
import json
import csv
import uuid
import re
import numpy as np
import gensim
import gensim.models.doc2vec
from sklearn.metrics.pairwise import cosine_similarity as cosine_sim

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
_cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
_cors_origins = [o.strip() for o in _cors_origins_env.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
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
        .order_by(asc(models.OriginRequirement.req_id))\
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
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            decoded = content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise HTTPException(400, "ไม่สามารถ decode ไฟล์ CSV ได้ กรุณาบันทึกไฟล์เป็น UTF-8 แล้วลองใหม่")
    reader = csv.DictReader(io.StringIO(decoded))

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
        .order_by(asc(models.AnalyzedRequirement.req_id))\
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
        .order_by(asc(models.SuggestedRequirement.req_id))\
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

@app.patch("/api/projects/{project_id}/selectedrequirements")
def upsert_single_selected_requirement(
    project_id: UUID,
    body: schemas.SelectedRequirementUpsert,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upsert a single requirement selection (delete old req_ids, insert new ones)."""
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if body.delete_req_ids:
        db.query(models.SelectedRequirement)\
            .filter(
                models.SelectedRequirement.project_id == project_id,
                models.SelectedRequirement.req_id.in_(body.delete_req_ids)
            ).delete(synchronize_session=False)

    objects = [
        models.SelectedRequirement(project_id=project_id, **req.dict())
        for req in body.insert
    ]
    db.bulk_save_objects(objects)
    db.commit()

    return {"deleted": len(body.delete_req_ids), "inserted": len(objects)}

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
        .order_by(asc(models.SelectedRequirement.req_id))\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return selecteds
@app.get("/api/projects/{project_id}/suggestedrequirements/similarity")
def get_similarity_summary(
    project_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Compute Jaccard Index and Doc2Vec cosine similarity between
    original_requirement and suggested_requirement for each non-split pair.
    """
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    rows = db.query(models.SuggestedRequirement).filter(
        models.SuggestedRequirement.project_id == project_id,
    ).order_by(asc(models.SuggestedRequirement.req_id)).all()

    if not rows:
        raise HTTPException(status_code=404, detail="No suggested requirements found")

    def tokenize(text: str) -> list:
        return re.findall(r'[\w\u0E00-\u0E7F]+', (text or '').lower())

    def jaccard_similarity(x, y):
        sx, sy = set(x), set(y)
        if not sx and not sy:
            return 1.0
        union = sx | sy
        if not union:
            return 0.0
        return len(sx & sy) / len(union)

    def get_suggested_text(row) -> str:
        if row.is_split and row.split_requirements:
            return ' '.join(s.get('requirement', '') for s in row.split_requirements)
        return row.suggested_requirement or ''

    orig_tokens = [tokenize(r.original_requirement) for r in rows]
    sugg_tokens = [tokenize(get_suggested_text(r)) for r in rows]

    # Train Doc2Vec on combined corpus
    all_tokens = orig_tokens + sugg_tokens

    def tagged_documents(token_lists):
        for i, tokens in enumerate(token_lists):
            yield gensim.models.doc2vec.TaggedDocument(tokens, [i])

    training_data = list(tagged_documents(all_tokens))
    model = gensim.models.doc2vec.Doc2Vec(vector_size=40, min_count=1, epochs=60)
    model.build_vocab(training_data)
    model.train(training_data, total_examples=model.corpus_count, epochs=model.epochs)

    n = len(rows)
    vectors = [model.infer_vector(tokens).reshape(1, -1) for tokens in all_tokens]

    def interpret(jaccard: float, emb: float) -> str:
        if emb >= 0.95:
            return 'เหมือนมาก'
        elif emb >= 0.80:
            return 'ความหมายใกล้เคียง'
        elif emb >= 0.60:
            return 'เปลี่ยนบางส่วน'
        else:
            return 'เปลี่ยนมาก'

    results = []
    for i, row in enumerate(rows):
        j = round(jaccard_similarity(orig_tokens[i], sugg_tokens[i]), 4)
        emb = round(float(cosine_sim(vectors[i], vectors[n + i])[0][0]), 4)
        results.append({
            "req_id": row.req_id,
            "original_score": row.original_score,
            "jaccard": j,
            "tfidf_sim": emb,
            "interpretation": interpret(j, emb),
            "is_split": bool(row.is_split),
        })

    jaccards = [r["jaccard"] for r in results]
    embeds = [r["tfidf_sim"] for r in results]

    summary = {
        "total": n,
        "jaccard": {
            "mean": round(float(np.mean(jaccards)), 4),
            "median": round(float(np.median(jaccards)), 4),
            "min": round(float(np.min(jaccards)), 4),
            "max": round(float(np.max(jaccards)), 4),
            "min_req": results[int(np.argmin(jaccards))]["req_id"],
            "max_req": results[int(np.argmax(jaccards))]["req_id"],
        },
        "tfidf": {
            "mean": round(float(np.mean(embeds)), 4),
            "median": round(float(np.median(embeds)), 4),
            "min": round(float(np.min(embeds)), 4),
            "max": round(float(np.max(embeds)), 4),
            "min_req": results[int(np.argmin(embeds))]["req_id"],
            "max_req": results[int(np.argmax(embeds))]["req_id"],
        },
        "interpretation_counts": {
            k: sum(1 for r in results if r["interpretation"] == k)
            for k in ["เหมือนมาก", "ความหมายใกล้เคียง", "เปลี่ยนบางส่วน", "เปลี่ยนมาก"]
        },
    }

    return {"summary": summary, "pairs": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)