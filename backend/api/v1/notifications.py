"""Notifications API: list, mark read, preferences."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import CurrentUser
from core.database import get_db

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("")
async def list_notifications(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    unread_only: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
) -> dict:
    from repositories.notification_repository import NotificationRepository
    repo = NotificationRepository(db)
    notifications, total = await repo.get_user_notifications(
        current_user.id, unread_only=unread_only,
        limit=page_size, offset=(page - 1) * page_size,
    )
    return {"notifications": notifications, "total": total, "unread_count": 0}


@router.post("/{notification_id}/read")
async def mark_read(
    notification_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    from repositories.notification_repository import NotificationRepository
    repo = NotificationRepository(db)
    await repo.mark_as_read(notification_id, current_user.id)
    return {"message": "Notification marked as read"}


@router.post("/read-all")
async def mark_all_read(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    from repositories.notification_repository import NotificationRepository
    repo = NotificationRepository(db)
    await repo.mark_all_read(current_user.id)
    return {"message": "All notifications marked as read"}
