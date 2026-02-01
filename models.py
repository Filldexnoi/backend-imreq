from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey , JSON , ARRAY , Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    requirement_template = Column(String(50), nullable=True)  # EARS, IEEE830, Others
    reference_files = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="projects")
    origin_requirements = relationship("OriginRequirement", back_populates="project", cascade="all, delete-orphan")
    analyzed_requirements = relationship("AnalyzedRequirement", back_populates="project", cascade="all, delete-orphan")
    suggested_requirements = relationship("SuggestedRequirement", back_populates="project", cascade="all, delete-orphan")
    selected_requirements = relationship("SelectedRequirement", back_populates="project", cascade="all, delete-orphan")

class OriginRequirement(Base):
    __tablename__ = "origin_requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    req_id = Column(String(50), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    module = Column(String(255), nullable=True)
    requirement = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    project = relationship("Project", back_populates="origin_requirements")

class AnalyzedRequirement(Base):
    __tablename__ = "analyzed_requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    req_id = Column(String(50), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    module = Column(String(255), nullable=True)
    score = Column(String(20), nullable=True)
    characteristics = Column(ARRAY(Text), nullable=True)
    requirement = Column(Text, nullable=False)
    evaluation = Column(JSON, nullable=True)  # Changed to JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    project = relationship("Project", back_populates="analyzed_requirements")

class SuggestedRequirement(Base):
    __tablename__ = "suggested_requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    req_id = Column(String(50), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    module = Column(String(255), nullable=True)
    original_requirement = Column(Text, nullable=False)  # Original requirement text
    suggested_requirement = Column(Text, nullable=False)  # Improved requirement text
    original_score = Column(String(20), nullable=True)  # Score before improvement
    improvements = Column(JSON, nullable=True)  # What was fixed for each criterion
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    project = relationship("Project", back_populates="suggested_requirements")

class SelectedRequirement(Base):
    __tablename__ = "selected_requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    req_id = Column(String(50), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    module = Column(String(255), nullable=True)
    requirement = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    project = relationship("Project", back_populates="selected_requirements")