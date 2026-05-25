"""Pydantic v2 schemas for Admin panel endpoints."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PlatformStatsResponse(BaseModel):
    total_users: int
    active_users_today: int
    active_users_week: int
    total_submissions_today: int
    total_submissions: int
    acceptance_rate: float
    total_problems: int
    total_contests: int
    active_labs: int
    revenue_month: float


class UserAdminResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    role: str
    status: str
    is_email_verified: bool
    login_attempts: int
    locked_until: datetime | None
    created_at: datetime
    last_login: datetime | None

    model_config = {"from_attributes": True}


class UserAdminListResponse(BaseModel):
    users: list[UserAdminResponse]
    total: int
    page: int
    per_page: int


class UpdateUserRoleRequest(BaseModel):
    role: str = Field(..., pattern="^(student|mentor|instructor|admin)$")
    reason: str | None = None


class BanUserRequest(BaseModel):
    reason: str = Field(..., min_length=10)
    duration_hours: int | None = Field(None, ge=1)


class SystemHealthResponse(BaseModel):
    api: str
    database: str
    redis: str
    kafka: str
    elasticsearch: str
    qdrant: str
    celery_workers: int
    queue_lengths: dict[str, int]


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None
    action: str
    ip_address: str | None
    success: bool
    failure_reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    logs: list[AuditLogResponse]
    total: int


class BroadcastNotificationRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    message: str = Field(..., max_length=2000)
    target: str = Field(default="all", pattern="^(all|premium|free)$")


class ProblemAdminCreate(BaseModel):
    title: str
    description: str
    difficulty: str
    problem_type: str
    tags: list[str] = []
    time_limit_ms: int = 2000
    memory_limit_mb: int = 256
    points: int = 100
    is_published: bool = False


class FeatureFlagUpdate(BaseModel):
    key: str
    enabled: bool
    description: str | None = None
