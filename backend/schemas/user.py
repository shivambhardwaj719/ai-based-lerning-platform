"""User request/response schemas."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    username: str
    full_name: str
    avatar_url: str | None
    bio: str | None
    website_url: str | None
    github_url: str | None
    linkedin_url: str | None
    country: str | None
    timezone: str
    role: str
    status: str
    subscription_tier: str
    is_email_verified: bool
    is_2fa_enabled: bool
    skills: list[str] | None
    preferred_languages: list[str] | None
    last_login_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    total_points: int
    problems_solved: int
    contests_participated: int
    contests_won: int
    streak_days: int
    max_streak_days: int
    rank: int | None
    rating: int
    level: int
    experience_points: int
    badges: list | None
    stats: dict | None

    class Config:
        from_attributes = True


class PublicUserResponse(BaseModel):
    id: uuid.UUID
    username: str
    full_name: str
    avatar_url: str | None
    bio: str | None
    country: str | None
    skills: list[str] | None
    created_at: datetime
    profile: UserProfileResponse | None

    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=255)
    bio: str | None = Field(None, max_length=2000)
    website_url: str | None = None
    github_url: str | None = None
    linkedin_url: str | None = None
    country: str | None = None
    timezone: str | None = None
    skills: list[str] | None = None
    preferred_languages: list[str] | None = None
    learning_goals: dict | None = None


class UpdateUsernameRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")


class UserListResponse(BaseModel):
    users: list[PublicUserResponse]
    total: int
    page: int
    page_size: int


class LeaderboardEntryResponse(BaseModel):
    rank: int
    user: PublicUserResponse
    score: float
    problems_solved: int
    rating: int
