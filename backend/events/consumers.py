"""
Kafka event consumers: process events from all services.
Each consumer group runs in its own background task.
"""
from __future__ import annotations

import asyncio
import json

import structlog

from core.kafka import Topics, kafka_manager
from core.redis import redis_manager

log = structlog.get_logger()


async def submission_consumer() -> None:
    """Consumes submission.created events and dispatches evaluation tasks."""
    consumer = kafka_manager.create_consumer(
        [Topics.SUBMISSION_CREATED],
        group_id="submission-evaluator",
    )
    await consumer.start()
    try:
        async for msg in consumer:
            try:
                data = msg.value
                submission_id = data.get("payload", {}).get("submission_id")
                if submission_id:
                    from workers.tasks.submission_tasks import evaluate_submission
                    evaluate_submission.delay(submission_id)
                    log.info("Dispatched evaluation", submission_id=submission_id)
                await consumer.commit()
            except Exception as e:
                log.error("Error processing submission event", error=str(e))
    finally:
        await consumer.stop()


async def notification_consumer() -> None:
    """Consumes notification.send events and delivers to users."""
    consumer = kafka_manager.create_consumer(
        [Topics.NOTIFICATION_SEND, Topics.EMAIL_SEND],
        group_id="notification-service",
    )
    await consumer.start()
    try:
        async for msg in consumer:
            try:
                data = msg.value
                event_type = data.get("event_type")
                payload = data.get("payload", {})

                if event_type == "email.send":
                    from workers.tasks.notification_tasks import send_email_task
                    send_email_task.delay(
                        to=payload.get("to"),
                        subject=payload.get("subject"),
                        template=payload.get("template"),
                        context=payload.get("context"),
                    )
                elif event_type == "notification.send":
                    # Push WebSocket notification
                    user_id = payload.get("user_id")
                    if user_id:
                        from websocket.manager import ws_manager
                        await ws_manager.send_to_user(user_id, {
                            "type": "notification",
                            "data": payload,
                        })

                await consumer.commit()
            except Exception as e:
                log.error("Notification error", error=str(e))
    finally:
        await consumer.stop()


async def analytics_consumer() -> None:
    """Consumes analytics events for real-time metrics."""
    consumer = kafka_manager.create_consumer(
        [Topics.ANALYTICS_EVENT, Topics.USER_ACTIVITY],
        group_id="analytics-service",
    )
    await consumer.start()
    try:
        async for msg in consumer:
            try:
                data = msg.value
                payload = data.get("payload", {})
                event_type = data.get("event_type", "")

                # Track in Redis for real-time dashboards
                await redis_manager.incr(f"analytics:events:{event_type}")
                await consumer.commit()
            except Exception as e:
                log.error("Analytics error", error=str(e))
    finally:
        await consumer.stop()


async def contest_consumer() -> None:
    """Processes contest events: leaderboard updates, notifications."""
    consumer = kafka_manager.create_consumer(
        [Topics.CONTEST_SUBMISSION, Topics.CONTEST_LEADERBOARD_UPDATED],
        group_id="contest-service",
    )
    await consumer.start()
    try:
        async for msg in consumer:
            try:
                data = msg.value
                payload = data.get("payload", {})
                event_type = data.get("event_type", "")
                contest_id = payload.get("contest_id")

                if contest_id and event_type == "contest.leaderboard_updated":
                    # Invalidate leaderboard cache
                    keys = [f"contest:leaderboard:{contest_id}:{p}" for p in range(1, 10)]
                    await redis_manager.delete(*keys)

                await consumer.commit()
            except Exception as e:
                log.error("Contest consumer error", error=str(e))
    finally:
        await consumer.stop()


async def start_all_consumers() -> None:
    """Start all Kafka consumers as background tasks."""
    log.info("Starting Kafka consumers")
    await asyncio.gather(
        submission_consumer(),
        notification_consumer(),
        analytics_consumer(),
        contest_consumer(),
        return_exceptions=True,
    )
