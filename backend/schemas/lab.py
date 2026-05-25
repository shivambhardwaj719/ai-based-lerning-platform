"""Pydantic v2 schemas for DevOps Lab endpoints."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class LabResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    category: str
    difficulty: str
    estimated_time: int
    tags: list[str]
    is_published: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class LabListResponse(BaseModel):
    labs: list[LabResponse]
    total: int
    page: int
    per_page: int


class StartLabRequest(BaseModel):
    lab_id: uuid.UUID


class LabInstanceResponse(BaseModel):
    id: uuid.UUID
    lab_id: uuid.UUID
    lab_title: str
    status: str
    access_url: str | None = None
    ssh_command: str | None = None
    expires_at: datetime
    started_at: datetime

    model_config = {"from_attributes": True}


class LabInstanceListResponse(BaseModel):
    instances: list[LabInstanceResponse]
    total: int


class ExtendLabRequest(BaseModel):
    extension_hours: int = Field(default=1, ge=1, le=4)


class AIPlaygroundCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    template: str = Field(default="python", pattern="^(python|nodejs|go|rust|general)$")


class AIPlaygroundResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    template: str
    jupyter_url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class LabProgressUpdate(BaseModel):
    step_index: int = Field(..., ge=0)
    completed: bool
    notes: str | None = None
