"""Pydantic v2 schemas for Contest endpoints."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ContestCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., max_length=5000)
    contest_type: str = Field(..., pattern="^(icpc|rated|unrated|practice)$")
    start_time: datetime
    end_time: datetime
    max_participants: int = Field(default=500, ge=1, le=10000)
    problem_ids: list[uuid.UUID] = Field(..., min_length=1, max_length=20)
    is_public: bool = True
    rating_floor: int | None = None
    rating_ceiling: int | None = None


class ContestUpdate(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=200)
    description: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    max_participants: int | None = None
    is_public: bool | None = None


class ContestResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    contest_type: str
    status: str
    start_time: datetime
    end_time: datetime
    max_participants: int
    participant_count: int
    is_public: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ContestListResponse(BaseModel):
    contests: list[ContestResponse]
    total: int
    page: int
    per_page: int


class JoinContestResponse(BaseModel):
    message: str
    contest_id: uuid.UUID
    registered_at: datetime


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: uuid.UUID
    username: str
    score: int
    problems_solved: int
    penalty: int
    last_accepted_at: datetime | None = None


class ContestLeaderboardResponse(BaseModel):
    contest_id: uuid.UUID
    entries: list[LeaderboardEntry]
    updated_at: datetime


class ContestStatsResponse(BaseModel):
    contest_id: uuid.UUID
    total_participants: int
    total_submissions: int
    total_accepted: int
    acceptance_rate: float
    problem_stats: list[dict[str, Any]]
