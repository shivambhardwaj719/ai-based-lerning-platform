"""Problems API: list, detail, submit, run, editorial."""
from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import CurrentUser, CurrentUserOptional, VerifiedUser
from auth.rbac import Permission, require_permission
from core.database import get_db
from core.exceptions import NotFoundError, SubmissionLimitExceededError
from core.kafka import Topics, kafka_manager
from core.redis import redis_manager
from models.problem import ProgrammingLanguage
from repositories.problem_repository import ProblemRepository, SubmissionRepository
from repositories.user_repository import UserRepository
from schemas.problem import (
    ProblemListResponse,
    ProblemResponse,
    RunCodeRequest,
    RunCodeResponse,
    SubmitCodeRequest,
    SubmissionDetailResponse,
    SubmissionResponse,
)

router = APIRouter(prefix="/problems", tags=["Problems"])


@router.get("", response_model=ProblemListResponse)
async def list_problems(
    current_user: CurrentUserOptional,
    db: AsyncSession = Depends(get_db),
    difficulty: str | None = Query(None, enum=["easy", "medium", "hard", "expert"]),
    tags: list[str] | None = Query(None),
    problem_type: str | None = None,
    is_premium: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> ProblemListResponse:
    repo = ProblemRepository(db)
    offset = (page - 1) * page_size
    problems, total = await repo.get_published_problems(
        difficulty=difficulty,
        tags=tags,
        problem_type=problem_type,
        is_premium=is_premium,
        limit=page_size,
        offset=offset,
    )

    # Enrich with solved status if authenticated
    solved_ids: set[uuid.UUID] = set()
    if current_user:
        sub_repo = SubmissionRepository(db)
        for p in problems:
            if await sub_repo.has_solved_problem(current_user.id, p.id):
                solved_ids.add(p.id)

    from schemas.problem import ProblemListItem
    items = [
        ProblemListItem(
            id=p.id, title=p.title, slug=p.slug, difficulty=p.difficulty,
            problem_type=p.problem_type, tags=p.tags, acceptance_rate=p.acceptance_rate,
            total_submissions=p.total_submissions, is_premium=p.is_premium,
            is_solved=p.id in solved_ids,
        )
        for p in problems
    ]
    return ProblemListResponse(problems=items, total=total, page=page, page_size=page_size)


@router.get("/{slug}", response_model=ProblemResponse)
async def get_problem(slug: str, db: AsyncSession = Depends(get_db)) -> ProblemResponse:
    repo = ProblemRepository(db)
    problem = await repo.get_by_slug(slug)
    if not problem:
        raise NotFoundError("Problem")
    sample_cases = await repo.get_sample_test_cases(problem.id)
    result = ProblemResponse.model_validate(problem)
    from schemas.problem import TestCaseResponse
    result.sample_test_cases = [TestCaseResponse.model_validate(tc) for tc in sample_cases]
    return result


@router.post("/submit", response_model=SubmissionResponse, status_code=202)
async def submit_code(
    body: SubmitCodeRequest,
    current_user: VerifiedUser,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> SubmissionResponse:
    # Rate limit: max 10 submissions per minute per user
    key = f"submit:rl:{current_user.id}"
    allowed, remaining = await redis_manager.rate_limit_check(key, limit=10, window=60)
    if not allowed:
        raise SubmissionLimitExceededError()

    # Verify problem exists
    problem_repo = ProblemRepository(db)
    problem = await problem_repo.get_by_id(body.problem_id)
    if not problem:
        raise NotFoundError("Problem")

    # Verify language is allowed
    if problem.allowed_languages and body.language not in problem.allowed_languages:
        from core.exceptions import ValidationError
        raise ValidationError(f"Language '{body.language}' not allowed for this problem")

    sub_repo = SubmissionRepository(db)
    submission = await sub_repo.create(
        user_id=current_user.id,
        problem_id=body.problem_id,
        contest_id=body.contest_id,
        code=body.code,
        language=body.language,
    )

    # Dispatch to code execution worker via Kafka
    await kafka_manager.publish(
        Topics.SUBMISSION_CREATED,
        "submission.created",
        {
            "submission_id": str(submission.id),
            "user_id": str(current_user.id),
            "problem_id": str(body.problem_id),
            "language": body.language,
            "code": body.code,
        },
        key=str(submission.id),
    )

    return SubmissionResponse.model_validate(submission)


@router.post("/run", response_model=RunCodeResponse)
async def run_code(
    body: RunCodeRequest,
    current_user: VerifiedUser,
    db: AsyncSession = Depends(get_db),
) -> RunCodeResponse:
    """Run code against sample test cases or custom input."""
    key = f"run:rl:{current_user.id}"
    allowed, _ = await redis_manager.rate_limit_check(key, limit=20, window=60)
    if not allowed:
        from core.exceptions import RateLimitExceededError
        raise RateLimitExceededError()

    problem_repo = ProblemRepository(db)
    problem = await problem_repo.get_by_id(body.problem_id)
    if not problem:
        raise NotFoundError("Problem")

    # Execute synchronously for run (smaller timeout)
    from apps.code_execution.executor import CodeExecutor
    executor = CodeExecutor()
    sample_cases = await problem_repo.get_sample_test_cases(body.problem_id)

    result = await executor.run(
        code=body.code,
        language=body.language,
        test_cases=[{"input": tc.input_data, "expected": tc.expected_output} for tc in sample_cases],
        custom_input=body.custom_input,
        time_limit_ms=problem.time_limit_ms,
        memory_limit_mb=problem.memory_limit_mb,
    )
    return RunCodeResponse(**result)


@router.get("/submissions/{submission_id}", response_model=SubmissionDetailResponse)
async def get_submission(
    submission_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> SubmissionDetailResponse:
    repo = SubmissionRepository(db)
    submission = await repo.get_by_id(submission_id)
    if not submission:
        raise NotFoundError("Submission")
    if submission.user_id != current_user.id:
        from auth.rbac import UserRole
        if current_user.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.INSTRUCTOR):
            raise NotFoundError("Submission")
    return SubmissionDetailResponse.model_validate(submission)


@router.get("/{slug}/submissions", response_model=list[SubmissionResponse])
async def get_my_submissions(
    slug: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
) -> list[SubmissionResponse]:
    problem_repo = ProblemRepository(db)
    problem = await problem_repo.get_by_slug(slug)
    if not problem:
        raise NotFoundError("Problem")

    sub_repo = SubmissionRepository(db)
    subs = await sub_repo.get_user_submissions(
        current_user.id, problem_id=problem.id,
        limit=page_size, offset=(page - 1) * page_size,
    )
    return [SubmissionResponse.model_validate(s) for s in subs]
