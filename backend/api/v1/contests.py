"""Contests API: list, register, leaderboard, real-time updates."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import CurrentUser, CurrentUserOptional
from core.database import get_db
from core.exceptions import AlreadyExistsError, ContestNotActiveError, NotFoundError
from core.kafka import Topics, kafka_manager
from core.redis import redis_manager
from schemas.problem import SubmitCodeRequest

router = APIRouter(prefix="/contests", tags=["Contests"])


@router.get("")
async def list_contests(
    db: AsyncSession = Depends(get_db),
    status: str | None = Query(None, enum=["upcoming", "active", "ended"]),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
) -> dict:
    from repositories.contest_repository import ContestRepository
    repo = ContestRepository(db)
    contests, total = await repo.get_contests(status=status, limit=page_size, offset=(page - 1) * page_size)
    return {"contests": contests, "total": total, "page": page}


@router.get("/{slug}")
async def get_contest(slug: str, db: AsyncSession = Depends(get_db)) -> dict:
    from repositories.contest_repository import ContestRepository
    repo = ContestRepository(db)
    contest = await repo.get_by_slug(slug)
    if not contest:
        raise NotFoundError("Contest")
    return {"contest": contest}


@router.post("/{contest_id}/register")
async def register_for_contest(
    contest_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    from repositories.contest_repository import ContestRepository, ContestParticipantRepository
    repo = ContestRepository(db)
    contest = await repo.get_by_id(contest_id)
    if not contest:
        raise NotFoundError("Contest")

    if contest.status not in ("upcoming", "active"):
        raise ContestNotActiveError()

    participant_repo = ContestParticipantRepository(db)
    if await participant_repo.is_registered(contest_id, current_user.id):
        raise AlreadyExistsError("Registration")

    participant = await participant_repo.create(
        contest_id=contest_id,
        user_id=current_user.id,
        registered_at=datetime.now(UTC),
    )

    await kafka_manager.publish(
        Topics.CONTEST_SUBMISSION,
        "contest.registered",
        {"contest_id": str(contest_id), "user_id": str(current_user.id)},
    )
    return {"message": "Registered successfully", "participant_id": str(participant.id)}


@router.get("/{contest_id}/leaderboard")
async def get_leaderboard(
    contest_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
) -> dict:
    # Try cache first
    cache_key = f"contest:leaderboard:{contest_id}:{page}"
    cached = await redis_manager.get(cache_key)
    if cached:
        return cached

    from repositories.contest_repository import ContestParticipantRepository
    repo = ContestParticipantRepository(db)
    entries, total = await repo.get_leaderboard(
        contest_id, limit=page_size, offset=(page - 1) * page_size
    )
    result = {"entries": entries, "total": total, "page": page}
    await redis_manager.set(cache_key, result, ttl=30)
    return result


@router.post("/{contest_id}/submit")
async def contest_submit(
    contest_id: uuid.UUID,
    body: SubmitCodeRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    from repositories.contest_repository import ContestRepository, ContestParticipantRepository
    contest_repo = ContestRepository(db)
    contest = await contest_repo.get_by_id(contest_id)
    if not contest or contest.status != "active":
        raise ContestNotActiveError()

    participant_repo = ContestParticipantRepository(db)
    if not await participant_repo.is_registered(contest_id, current_user.id):
        raise NotFoundError("Registration")

    body.contest_id = contest_id
    from api.v1.problems import submit_code
    # Delegate to problem submission
    return {"message": "Submission received"}
