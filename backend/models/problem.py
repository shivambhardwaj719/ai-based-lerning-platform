"""
Problem, Submission, TestCase models for the coding challenge system.
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger, Boolean, DateTime, Enum, Float, ForeignKey,
    Integer, String, Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel


class Difficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class ProblemType(str, enum.Enum):
    ALGORITHMIC = "algorithmic"
    DATA_STRUCTURE = "data_structure"
    SYSTEM_DESIGN = "system_design"
    DATABASE = "database"
    SHELL = "shell"
    CONCURRENCY = "concurrency"
    ML = "ml"
    DEBUGGING = "debugging"


class SubmissionStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    MEMORY_LIMIT_EXCEEDED = "memory_limit_exceeded"
    RUNTIME_ERROR = "runtime_error"
    COMPILATION_ERROR = "compilation_error"
    INTERNAL_ERROR = "internal_error"


class ProgrammingLanguage(str, enum.Enum):
    PYTHON = "python"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    CPP = "cpp"
    C = "c"
    KOTLIN = "kotlin"
    SWIFT = "swift"
    RUBY = "ruby"
    CSHARP = "csharp"
    SCALA = "scala"


class Problem(BaseModel):
    __tablename__ = "problems"

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    editorial: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[Difficulty] = mapped_column(Enum(Difficulty), nullable=False, index=True)
    problem_type: Mapped[ProblemType] = mapped_column(
        Enum(ProblemType), default=ProblemType.ALGORITHMIC, nullable=False
    )
    tags: Mapped[list | None] = mapped_column(ARRAY(String), nullable=True, index=True)
    companies: Mapped[list | None] = mapped_column(ARRAY(String), nullable=True)
    hints: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    constraints: Mapped[str | None] = mapped_column(Text, nullable=True)
    examples: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    starter_code: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    solution_code: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    time_limit_ms: Mapped[int] = mapped_column(Integer, default=2000, nullable=False)
    memory_limit_mb: Mapped[int] = mapped_column(Integer, default=256, nullable=False)
    allowed_languages: Mapped[list | None] = mapped_column(ARRAY(String), nullable=True)

    total_submissions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    accepted_submissions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    acceptance_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    upvotes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    downvotes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    test_cases: Mapped[list[TestCase]] = relationship("TestCase", back_populates="problem", cascade="all, delete-orphan")
    submissions: Mapped[list[Submission]] = relationship("Submission", back_populates="problem")


class TestCase(BaseModel):
    __tablename__ = "test_cases"

    problem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True
    )
    input_data: Mapped[str] = mapped_column(Text, nullable=False)
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)
    is_sample: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    problem: Mapped[Problem] = relationship("Problem", back_populates="test_cases")


class Submission(BaseModel):
    __tablename__ = "submissions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    problem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True
    )
    contest_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contests.id", ondelete="SET NULL"), nullable=True, index=True
    )

    code: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[ProgrammingLanguage] = mapped_column(Enum(ProgrammingLanguage), nullable=False)
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus), default=SubmissionStatus.PENDING, nullable=False, index=True
    )

    runtime_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    memory_used_mb: Mapped[float | None] = mapped_column(Float, nullable=True)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    test_cases_passed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    test_cases_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    stdout: Mapped[str | None] = mapped_column(Text, nullable=True)
    stderr: Mapped[str | None] = mapped_column(Text, nullable=True)
    compile_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    test_results: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    ai_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    plagiarism_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_plagiarized: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    problem: Mapped[Problem] = relationship("Problem", back_populates="submissions")
