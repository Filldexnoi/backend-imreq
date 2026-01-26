from pydantic import BaseModel, field_validator
from typing import List, Optional , Dict , Any
from datetime import datetime
from uuid import UUID

# Project Schemas
class ProjectBase(BaseModel):
    title: str
    description: str

class ProjectCreate(ProjectBase):
    requirement_template: Optional[str] = "Others"
    reference_files: Optional[List[Dict[str, Any]]] = None

class ProjectUpdate(ProjectBase):
    title: Optional[str] = None
    description: Optional[str] = None
    requirement_template: Optional[str] = None
    reference_files: Optional[List[Dict[str, Any]]] = None

class Project(ProjectBase):
    id: UUID
    requirement_template: Optional[str] = None
    reference_files: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator('reference_files', mode='before')
    @classmethod
    def validate_reference_files(cls, v):
        if v is None:
            return None
        
        # If it's already a list of dicts, check format
        if isinstance(v, list):
            normalized = []
            for item in v:
                if isinstance(item, dict):
                    # New format: {name, content, size, type}
                    if 'content' in item:
                        normalized.append(item)
                    # Old format: {original_name, stored_name, path, size}
                    # Convert to new format or skip
                    elif 'original_name' in item:
                        # Skip old format files (they're on filesystem)
                        continue
                    else:
                        normalized.append(item)
            return normalized if normalized else None
        
        return v

    class Config:
        from_attributes = True

class ResponseProjectCreate(BaseModel):
    id : UUID

# Requirement Schemas
class OriginRequirementBase(BaseModel):
    req_id: str
    module: str
    requirement: str

class OriginRequirementCreate(OriginRequirementBase):
    project_id: UUID

class OriginRequirement(OriginRequirementBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ResponseOriginRequirementCreate(BaseModel):
    inserted_rows : int

# Analyzed Requirement Schemas
class AnalyzedRequirementBase(BaseModel):
    req_id: str
    module: str
    requirement: str
    score: Optional[str] = None
    characteristics: Optional[List[str]] = None  # เปลี่ยนจาก str เป็น List[str]
    evaluation: Optional[Dict[str, Any]] = None  # เปลี่ยนจาก str เป็น Dict

class AnalyzedRequirementCreate(AnalyzedRequirementBase):
    project_id: UUID

class AnalyzedRequirement(AnalyzedRequirementBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Suggested Requirement Schemas
class SuggestedRequirementBase(BaseModel):
    req_id: str
    module: str
    original_requirement: str
    suggested_requirement: str
    original_score: Optional[str] = None
    improvements: Optional[Dict[str, str]] = None  # What was fixed for each criterion

class SuggestedRequirementCreate(SuggestedRequirementBase):
    project_id: UUID

class SuggestedRequirement(SuggestedRequirementBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Selected Requirement Schemas
class SelectedRequirementBase(BaseModel):
    req_id: str
    module: str
    requirement: str

class SelectedRequirementCreate(SelectedRequirementBase):
    project_id: UUID

class SelectedRequirement(SelectedRequirementBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Column Mapping Schema
class ColumnMapping(BaseModel):
    req_id: str
    module: str
    requirement: str

# Response Schemas
class FileUploadResponse(BaseModel):
    filename: str
    columns: List[str]
    row_count: int

class FileProcessResponse(BaseModel):
    message: str
    count: int