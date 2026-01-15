from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey , JSON , ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    origin_requirements = relationship("OriginRequirement", back_populates="project", cascade="all, delete-orphan")
    analyzed_requirements = relationship("AnalyzedRequirement", back_populates="project", cascade="all, delete-orphan")

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