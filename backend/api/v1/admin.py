"""Admin API: user management, content moderation, system stats."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import AdminUser
from core.database import get_db

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
async def system_stats(admin: AdminUser, db: AsyncSession = Depends(get_db)) -> dict:
    from repositories.user_repository import UserRepository
    from repositories.problem_repository import SubmissionRepository
    user_repo = UserRepository(db)
    total_users = await user_repo.count()
    return {
        "total_users": total_users,
        "active_users_today": 0,
        "total_submissions_today": 0,
        "active_contests": 0,
        "active_lab_instances": 0,
    }


@router.get("/users")
async def admin_list_users(
    admin: AdminUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    role: str | None = None,
) -> dict:
    from repositories.user_repository import UserRepository
    repo = UserRepository(db)
    filters = []
    if status:
        from models.user import UserStatus
        filters.append(UserStatus(status))
    users = await repo.get_all(limit=page_size, offset=(page - 1) * page_size)
    total = await repo.count()
    return {"users": users, "total": total, "page": page}


@router.post("/users/{user_id}/suspend")
async def suspend_user(
    user_id: uuid.UUID,
    body: dict,
    admin: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    from repositories.user_repository import UserRepository, SessionRepository
    from models.user import UserStatus
    repo = UserRepository(db)
    await repo.update(user_id, status=UserStatus.SUSPENDED)
    session_repo = SessionRepository(db)
    await session_repo.revoke_all_sessions(user_id)
    return {"message": "User suspended"}


@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: uuid.UUID,
    admin: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    from repositories.user_repository import UserRepository
    from models.user import UserStatus
    repo = UserRepository(db)
    await repo.update(user_id, status=UserStatus.ACTIVE)
    return {"message": "User activated"}


@router.get("/audit-logs")
async def get_audit_logs(
    admin: AdminUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    action: str | None = None,
) -> dict:
    from repositories.user_repository import AuditLogRepository
    from models.user import AuditLog
    repo = AuditLogRepository(db)
    filters = []
    if action:
        filters.append(AuditLog.action == action)
    logs = await repo.get_all(
        filters=filters or None,
        order_by=[AuditLog.created_at.desc()],
        limit=page_size,
        offset=(page - 1) * page_size,
    )
    total = await repo.count(filters=filters or None)
    return {"logs": logs, "total": total}
