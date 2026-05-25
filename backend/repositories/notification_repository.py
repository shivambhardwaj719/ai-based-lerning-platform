"""Notification repository stub."""
from __future__ import annotations

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.base import BaseRepository
from core.database import Base


class Notification(Base):
    """Placeholder - notifications stored in Redis/Kafka for now."""
    __tablename__ = "notifications"
    __table_args__ = {"extend_existing": True}
    from sqlalchemy.dialects.postgresql import UUID
    from sqlalchemy import Column, String, Boolean, DateTime, Text
    import sqlalchemy as sa
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = sa.Column(UUID(as_uuid=True), nullable=False, index=True)
    type = sa.Column(String(100), nullable=False)
    title = sa.Column(String(300), nullable=False)
    message = sa.Column(Text, nullable=True)
    is_read = sa.Column(Boolean, default=False)
    created_at = sa.Column(DateTime(timezone=True), server_default=sa.func.now())


class NotificationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_user_notifications(self, user_id: uuid.UUID, unread_only: bool = False,
                                      limit: int = 20, offset: int = 0) -> tuple[list, int]:
        return [], 0

    async def mark_as_read(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> None:
        pass

    async def mark_all_read(self, user_id: uuid.UUID) -> None:
        pass
