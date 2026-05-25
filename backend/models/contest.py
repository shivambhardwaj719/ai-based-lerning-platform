"""
Contest, ContestParticipant, and Leaderboard models.
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel


class ContestStatus(str, enum.Enum):
    DRAFT = "draft"
    UPCOMING = "upcoming"
    ACTIVE = "active"
    ENDED = "ended"
    CANCELLED = "cancelled"


class ContestType(str, enum.Enum):
    ICPC = "icpc"
    IOI = "ioi"
    RATED = "rated"
    UNRATED = "unrated"
    HACKATHON = "hackathon"
    AI_CHALLENGE = "ai_challenge"


class Contest(BaseModel):
    __tablename__ = "contests"

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    rules: Mapped[str | None] = mapped_column(Text, nullable=True)
    prizes: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    contest_type: Mapped[ContestType] = mapped_column(
        Enum(ContestType), default=ContestType.RATED, nullable=False
    )
    status: Mapped[ContestStatus] = mapped_column(
        Enum(ContestStatus), default=ContestStatus.DRAFT, nullable=False, index=True
    )

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    registration_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    max_participants: Mapped[int | None] = mapped_column(Integer, nullable=True)
    min_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_rated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_team_contest: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    max_team_size: Mapped[int | None] = mapped_column(Integer, nullable=True)

    banner_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    allowed_languages: Mapped[list | None] = mapped_column(ARRAY(String), nullable=True)
    scoring_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    total_participants: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    participants: Mapped[list[ContestParticipant]] = relationship(
        "ContestParticipant", back_populates="contest", cascade="all, delete-orphan"
    )
    problems: Mapped[list[ContestProblem]] = relationship(
        "ContestProblem", back_populates="contest", cascade="all, delete-orphan"
    )


class ContestProblem(BaseModel):
    __tablename__ = "contest_problems"

    contest_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contests.id", ondelete="CASCADE"), nullable=False
    )
    problem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False
    )
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    partial_scoring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    contest: Mapped[Contest] = relationship("Contest", back_populates="problems")


class ContestParticipant(BaseModel):
    __tablename__ = "contest_participants"

    contest_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contests.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    penalty_time: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    problems_solved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_disqualified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    disqualification_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    rating_change: Mapped[int | None] = mapped_column(Integer, nullable=True)
    registered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    contest: Mapped[Contest] = relationship("Contest", back_populates="participants")


class Leaderboard(BaseModel):
    __tablename__ = "leaderboards"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    leaderboard_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    period: Mapped[str] = mapped_column(String(20), nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
