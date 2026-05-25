"""Pydantic v2 schemas for Notification endpoints."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: uuid.UUID
    type: str
    title: str
    message: str | None = None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    total: int
    unread_count: int


class MarkReadRequest(BaseModel):
    notification_ids: list[uuid.UUID]


class PushSubscriptionCreate(BaseModel):
    endpoint: str
    keys: dict[str, str]


class NotificationPreferences(BaseModel):
    email_on_submission_result: bool = True
    email_on_contest_start: bool = True
    email_on_new_message: bool = True
    push_enabled: bool = False
    contest_reminders: bool = True
    weekly_digest: bool = True
