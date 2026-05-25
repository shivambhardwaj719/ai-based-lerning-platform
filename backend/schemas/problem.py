"""Problem and Submission schemas."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TestCaseResponse(BaseModel):
    id: uuid.UUID
    input_data: str
    expected_output: str
    is_sample: bool
    explanation: str | None
    order_index: int

    class Config:
        from_attributes = True


class ProblemResponse(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    description: str
    difficulty: str
    problem_type: str
    tags: list[str] | None
    companies: list[str] | None
    hints: list | None
    constraints: str | None
    examples: list | None
    starter_code: dict | None
    time_limit_ms: int
    memory_limit_mb: int
    allowed_languages: list[str] | None
    total_submissions: int
    accepted_submissions: int
    acceptance_rate: float
    upvotes: int
    is_premium: bool
    is_ai_generated: bool
    created_at: datetime
    sample_test_cases: list[TestCaseResponse] | None = None

    class Config:
        from_attributes = True


class ProblemListItem(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    difficulty: str
    problem_type: str
    tags: list[str] | None
    acceptance_rate: float
    total_submissions: int
    is_premium: bool
    is_solved: bool = False

    class Config:
        from_attributes = True


class ProblemListResponse(BaseModel):
    problems: list[ProblemListItem]
    total: int
    page: int
    page_size: int


class SubmitCodeRequest(BaseModel):
    problem_id: uuid.UUID
    code: str = Field(min_length=1, max_length=65536)
    language: str
    contest_id: uuid.UUID | None = None


class RunCodeRequest(BaseModel):
    problem_id: uuid.UUID
    code: str = Field(min_length=1, max_length=65536)
    language: str
    custom_input: str | None = None


class SubmissionResponse(BaseModel):
    id: uuid.UUID
    problem_id: uuid.UUID
    language: str
    status: str
    runtime_ms: int | None
    memory_used_mb: float | None
    score: float
    test_cases_passed: int
    test_cases_total: int
    ai_feedback: str | None
    ai_score: float | None
    created_at: datetime

    class Config:
        from_attributes = True


class SubmissionDetailResponse(SubmissionResponse):
    code: str
    stdout: str | None
    stderr: str | None
    compile_error: str | None
    test_results: list | None


class RunCodeResponse(BaseModel):
    status: str
    stdout: str | None
    stderr: str | None
    runtime_ms: int | None
    memory_used_mb: float | None
    test_results: list | None
