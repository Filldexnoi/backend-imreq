from pydantic import BaseModel, field_validator , EmailStr 
from typing import List, Optional , Dict , Any 
from datetime import datetime
from uuid import UUID


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password too long (max 72 bytes)')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if v is None:
            return v
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password too long (max 72 bytes)')
        return v
        
class User(UserBase):
    id: UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class TokenData(BaseModel):
    user_id: Optional[UUID] = None
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

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
    suggested_requirement: Optional[str] = None  # Null if split
    original_score: Optional[str] = None
    improvements: Optional[Dict[str, Any]] = None  # What was fixed for each criterion (str or {description, cited_rules})
    is_split: Optional[bool] = False  # True if requirement was split
    split_requirements: Optional[List[Dict[str, Any]]] = None  # Array of split requirements

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

class SelectedRequirementUpsert(BaseModel):
    delete_req_ids: List[str]
    insert: List[SelectedRequirementBase]

class SelectedRequirement(SelectedRequirementBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Column Mapping Schema
class ColumnMapping(BaseModel):
    requirement: str              # Required
    req_id: Optional[str] = None  # Optional
    module: Optional[str] = None  # Optional

# Response Schemas
class FileUploadResponse(BaseModel):
    filename: str
    columns: List[str]
    row_count: int

class FileProcessResponse(BaseModel):
    message: str
    count: int