"""
DevOps Lab, AI/ML Playground, and System Design Lab models.
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel


class LabType(str, enum.Enum):
    DEVOPS = "devops"
    AI_ML = "ai_ml"
    SYSTEM_DESIGN = "system_design"
    DATABASE = "database"
    NETWORKING = "networking"
    SECURITY = "security"
    CLOUD = "cloud"


class LabStatus(str, enum.Enum):
    PENDING = "pending"
    PROVISIONING = "provisioning"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class Lab(BaseModel):
    __tablename__ = "labs"

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    lab_type: Mapped[LabType] = mapped_column(Enum(LabType), nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    objectives: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    tasks: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    setup_script: Mapped[str | None] = mapped_column(Text, nullable=True)
    teardown_script: Mapped[str | None] = mapped_column(Text, nullable=True)
    docker_compose_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    k8s_manifests: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    estimated_duration_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    max_duration_minutes: Mapped[int] = mapped_column(Integer, default=120, nullable=False)
    tags: Mapped[list | None] = mapped_column(ARRAY(String), nullable=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resource_requirements: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    instances: Mapped[list[LabInstance]] = relationship(
        "LabInstance", back_populates="lab", cascade="all, delete-orphan"
    )


class LabInstance(BaseModel):
    __tablename__ = "lab_instances"

    lab_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("labs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[LabStatus] = mapped_column(
        Enum(LabStatus), default=LabStatus.PENDING, nullable=False, index=True
    )
    container_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    namespace: Mapped[str | None] = mapped_column(String(255), nullable=True)
    access_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    credentials: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    progress_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    tasks_completed: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    lab: Mapped[Lab] = relationship("Lab", back_populates="instances")


class AIPlayground(BaseModel):
    __tablename__ = "ai_playgrounds"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_type: Mapped[str] = mapped_column(String(100), nullable=False)
    configuration: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    code: Mapped[str | None] = mapped_column(Text, nullable=True)
    dataset: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    results: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
