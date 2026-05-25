"""
AI Conversation, Message, and Roadmap models.
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel


class ConversationType(str, enum.Enum):
    MENTOR = "mentor"
    PROBLEM_HELP = "problem_help"
    CODE_REVIEW = "code_review"
    INTERVIEW_PREP = "interview_prep"
    ROADMAP_PLANNING = "roadmap_planning"
    DEBUGGING = "debugging"
    GENERAL = "general"


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class AIConversation(BaseModel):
    __tablename__ = "ai_conversations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    conversation_type: Mapped[ConversationType] = mapped_column(
        Enum(ConversationType), default=ConversationType.GENERAL, nullable=False
    )
    context: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    total_tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    model_used: Mapped[str | None] = mapped_column(String(100), nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    messages: Mapped[list[AIMessage]] = relationship(
        "AIMessage", back_populates="conversation", cascade="all, delete-orphan"
    )


class AIMessage(BaseModel):
    __tablename__ = "ai_messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_conversations.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tool_calls: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    tool_results: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    feedback: Mapped[str | None] = mapped_column(String(20), nullable=True)  # thumbs_up/down
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    conversation: Mapped[AIConversation] = relationship("AIConversation", back_populates="messages")


class Roadmap(BaseModel):
    __tablename__ = "roadmaps"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    target_role: Mapped[str | None] = mapped_column(String(200), nullable=True)
    estimated_weeks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_week: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    progress_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    nodes: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    edges: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    skills_required: Mapped[list | None] = mapped_column(ARRAY(String), nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)


class StudyMaterial(BaseModel):
    __tablename__ = "study_materials"

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    topic: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    subtopic: Mapped[str | None] = mapped_column(String(200), nullable=True)
    difficulty_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    tags: Mapped[list | None] = mapped_column(ARRAY(String), nullable=True)
    estimated_read_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    embedding_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
