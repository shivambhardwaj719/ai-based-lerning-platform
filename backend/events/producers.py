"""Convenience wrappers for publishing domain events to Kafka topics."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

from core.kafka import Topics, kafka_manager

log = structlog.get_logger()


async def _publish(topic: str, data: dict[str, Any], key: str | None = None) -> None:
    await kafka_manager.publish(topic=topic, data=data, key=key)


# ---------- Submission events ----------

async def submission_created(
    submission_id: str,
    user_id: str,
    problem_id: str,
    language: str,
    code: str,
) -> None:
    await _publish(
        Topics.SUBMISSION_CREATED,
        {
            "submission_id": submission_id,
            "user_id": user_id,
            "problem_id": problem_id,
            "language": language,
            "code": code,
            "timestamp": datetime.now(UTC).isoformat(),
        },
        key=submission_id,
    )
    log.info("Event: submission_created", submission_id=submission_id)


async def submission_completed(
    submission_id: str,
    user_id: str,
    status: str,
    execution_time: float,
    memory_used: int,
) -> None:
    await _publish(
        Topics.SUBMISSION_COMPLETED,
        {
            "submission_id": submission_id,
            "user_id": user_id,
            "status": status,
            "execution_time": execution_time,
            "memory_used": memory_used,
            "timestamp": datetime.now(UTC).isoformat(),
        },
        key=submission_id,
    )
    log.info("Event: submission_completed", submission_id=submission_id, status=status)


# ---------- Notification events ----------

async def send_notification(
    user_id: str,
    notification_type: str,
    title: str,
    message: str,
    data: dict[str, Any] | None = None,
) -> None:
    await _publish(
        Topics.NOTIFICATION_SEND,
        {
            "user_id": user_id,
            "type": notification_type,
            "title": title,
            "message": message,
            "data": data or {},
            "timestamp": datetime.now(UTC).isoformat(),
        },
        key=user_id,
    )


# ---------- Contest events ----------

async def contest_started(contest_id: str, title: str, end_time: str) -> None:
    await _publish(
        Topics.CONTEST_STARTED,
        {
            "contest_id": contest_id,
            "title": title,
            "end_time": end_time,
            "timestamp": datetime.now(UTC).isoformat(),
        },
        key=contest_id,
    )
    log.info("Event: contest_started", contest_id=contest_id)


async def contest_ended(contest_id: str) -> None:
    await _publish(
        Topics.CONTEST_ENDED,
        {
            "contest_id": contest_id,
            "timestamp": datetime.now(UTC).isoformat(),
        },
        key=contest_id,
    )


# ---------- Payment events ----------

async def payment_completed(
    user_id: str,
    plan_id: str,
    subscription_id: str,
    amount: float,
    currency: str,
) -> None:
    await _publish(
        Topics.PAYMENT_COMPLETED,
        {
            "user_id": user_id,
            "plan_id": plan_id,
            "subscription_id": subscription_id,
            "amount": amount,
            "currency": currency,
            "timestamp": datetime.now(UTC).isoformat(),
        },
        key=user_id,
    )
    log.info("Event: payment_completed", user_id=user_id, plan_id=plan_id)


# ---------- Lab events ----------

async def lab_started(user_id: str, lab_id: str, instance_id: str) -> None:
    await _publish(
        Topics.LAB_STARTED,
        {
            "user_id": user_id,
            "lab_id": lab_id,
            "instance_id": instance_id,
            "timestamp": datetime.now(UTC).isoformat(),
        },
        key=instance_id,
    )


# ---------- User events ----------

async def user_registered(user_id: str, email: str, username: str) -> None:
    await _publish(
        "user.registered",
        {
            "user_id": user_id,
            "email": email,
            "username": username,
            "timestamp": datetime.now(UTC).isoformat(),
        },
        key=user_id,
    )
