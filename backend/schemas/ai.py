"""AI service schemas: conversations, roadmaps, mentor."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)
    conversation_id: uuid.UUID | None = None
    conversation_type: str = "general"
    context: dict | None = None
    stream: bool = True


class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    message_id: uuid.UUID
    content: str
    role: str = "assistant"
    tokens_used: int
    model: str
    created_at: datetime


class ConversationResponse(BaseModel):
    id: uuid.UUID
    title: str | None
    conversation_type: str
    created_at: datetime
    updated_at: datetime
    total_tokens_used: int

    class Config:
        from_attributes = True


class ConversationDetailResponse(ConversationResponse):
    messages: list[MessageResponse]


class MessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    tokens_used: int
    created_at: datetime
    feedback: str | None

    class Config:
        from_attributes = True


class RoadmapGenerateRequest(BaseModel):
    goal: str = Field(min_length=10, max_length=2000)
    target_role: str | None = None
    current_skills: list[str] = []
    experience_level: str = "beginner"
    available_hours_per_week: int = Field(default=10, ge=1, le=80)
    timeline_weeks: int | None = Field(None, ge=4, le=104)
    learning_style: str = "balanced"


class RoadmapResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    goal: str
    target_role: str | None
    estimated_weeks: int | None
    current_week: int
    progress_percentage: float
    is_ai_generated: bool
    nodes: list | None
    edges: list | None
    created_at: datetime

    class Config:
        from_attributes = True


class ProblemGenerateRequest(BaseModel):
    topic: str
    difficulty: str = "medium"
    problem_type: str = "algorithmic"
    tags: list[str] = []
    count: int = Field(default=1, ge=1, le=5)


class CodeReviewRequest(BaseModel):
    code: str = Field(min_length=1, max_length=65536)
    language: str
    problem_context: str | None = None
    focus_areas: list[str] = []


class CodeReviewResponse(BaseModel):
    overall_score: float
    feedback: str
    issues: list[dict]
    suggestions: list[str]
    optimizations: list[dict]
    best_practices: list[str]
    time_complexity: str | None
    space_complexity: str | None


class InterviewSessionRequest(BaseModel):
    interview_type: str
    role: str
    experience_level: str
    topics: list[str] = []
    duration_minutes: int = Field(default=45, ge=15, le=120)


class InterviewSessionResponse(BaseModel):
    session_id: uuid.UUID
    question: str
    hints: list[str]
    expected_approach: str
    time_limit_minutes: int
