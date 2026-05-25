"""Users API: profile, settings, leaderboard, achievements."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import CurrentUser, AdminUser
from core.database import get_db
from core.exceptions import NotFoundError
from repositories.user_repository import UserRepository
from schemas.user import (
    LeaderboardEntryResponse,
    PublicUserResponse,
    UpdateProfileRequest,
    UpdateUsernameRequest,
    UserListResponse,
    UserResponse,
    UserProfileResponse,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    body: UpdateProfileRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    repo = UserRepository(db)
    updates = body.model_dump(exclude_none=True)
    if updates:
        await repo.update(current_user.id, **updates)
    updated = await repo.get_by_id(current_user.id)
    return UserResponse.model_validate(updated)


@router.patch("/me/username")
async def change_username(
    body: UpdateUsernameRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    repo = UserRepository(db)
    if await repo.username_exists(body.username):
        from core.exceptions import AlreadyExistsError
        raise AlreadyExistsError("Username")
    await repo.update(current_user.id, username=body.username)
    return {"message": "Username updated"}


@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
) -> dict:
    from utils.storage import upload_file
    url = await upload_file(file, folder=f"avatars/{current_user.id}")
    repo = UserRepository(db)
    await repo.update(current_user.id, avatar_url=url)
    return {"avatar_url": url}


@router.get("/me/profile", response_model=UserProfileResponse)
async def get_my_profile(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> UserProfileResponse:
    repo = UserRepository(db)
    user = await repo.get_with_profile(current_user.id)
    if not user or not user.profile:
        raise NotFoundError("Profile")
    return UserProfileResponse.model_validate(user.profile)


@router.get("/{username}", response_model=PublicUserResponse)
async def get_user(username: str, db: AsyncSession = Depends(get_db)) -> PublicUserResponse:
    repo = UserRepository(db)
    user = await repo.get_with_profile(
        (await repo.get_by_username(username)).id if await repo.get_by_username(username) else None
    ) if True else None

    user = await repo.get_by_username(username)
    if not user:
        raise NotFoundError("User")
    user_with_profile = await repo.get_with_profile(user.id)
    return PublicUserResponse.model_validate(user_with_profile)


@router.get("", response_model=UserListResponse)
async def list_users(
    admin: AdminUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> UserListResponse:
    repo = UserRepository(db)
    users = await repo.get_all(limit=page_size, offset=(page - 1) * page_size)
    total = await repo.count()
    return UserListResponse(
        users=[PublicUserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/leaderboard/global", response_model=list[LeaderboardEntryResponse])
async def global_leaderboard(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
) -> list[LeaderboardEntryResponse]:
    from core.redis import redis_manager
    cache_key = f"leaderboard:global:{page}"
    cached = await redis_manager.get(cache_key)
    if cached:
        return cached
    # Build from Redis sorted set
    entries = await redis_manager.zrevrange("leaderboard:global", 0, -1, withscores=True)
    return []
