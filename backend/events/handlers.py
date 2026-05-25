"""Domain event handlers — called by Kafka consumers after message deserialization."""
from __future__ import annotations

from typing import Any

import structlog

log = structlog.get_logger()


async def handle_submission_created(data: dict[str, Any]) -> None:
    """Dispatch Celery task to evaluate the submission."""
    from workers.tasks.submission_tasks import evaluate_submission
    submission_id = data["submission_id"]
    evaluate_submission.delay(submission_id)
    log.info("Dispatched evaluate_submission", submission_id=submission_id)


async def handle_submission_completed(data: dict[str, Any]) -> None:
    """Fan-out: update analytics, trigger AI feedback, notify via WebSocket."""
    from workers.tasks.ai_tasks import generate_ai_feedback
    from workers.tasks.analytics_tasks import update_global_leaderboard

    submission_id = data["submission_id"]
    user_id = data["user_id"]
    status = data.get("status")

    # Trigger AI feedback for accepted submissions
    if status == "accepted":
        generate_ai_feedback.delay(submission_id)
        update_global_leaderboard.apply_async(countdown=60)  # debounce 60s

    # Notify user via WebSocket (fire-and-forget)
    try:
        from core.redis import redis_manager
        await redis_manager.publish(
            f"ws:submission:{submission_id}",
            {"type": "submission_result", **data},
        )
    except Exception:
        log.warning("Failed to publish WS notification", submission_id=submission_id)


async def handle_notification_send(data: dict[str, Any]) -> None:
    """Route notification to email / push / WebSocket based on type."""
    from workers.tasks.notification_tasks import send_email_notification, send_push_notification

    notification_type = data.get("type", "")
    user_id = data["user_id"]

    if notification_type in ("email_verify", "password_reset", "otp"):
        send_email_notification.delay(
            user_id=user_id,
            subject=data.get("title", ""),
            body=data.get("message", ""),
            template=notification_type,
            template_data=data.get("data", {}),
        )
    else:
        # In-app / push notification
        send_push_notification.delay(user_id=user_id, payload=data)

    # Always try WebSocket delivery for real-time
    try:
        from core.redis import redis_manager
        await redis_manager.publish(f"ws:notifications:{user_id}", data)
    except Exception:
        pass


async def handle_payment_completed(data: dict[str, Any]) -> None:
    """Activate subscription and notify user."""
    from workers.tasks.payment_tasks import activate_subscription
    activate_subscription.delay(
        user_id=data["user_id"],
        subscription_id=data["subscription_id"],
        plan_id=data["plan_id"],
    )
    log.info("Dispatched activate_subscription", user_id=data["user_id"])


async def handle_contest_started(data: dict[str, Any]) -> None:
    """Notify all participants that contest has begun."""
    from workers.tasks.notification_tasks import notify_contest_participants
    notify_contest_participants.delay(
        contest_id=data["contest_id"],
        message=f"Contest '{data['title']}' has started!",
    )


async def handle_lab_started(data: dict[str, Any]) -> None:
    """Provision the lab environment."""
    from workers.tasks.lab_tasks import provision_lab
    provision_lab.delay(
        instance_id=data["instance_id"],
        lab_id=data["lab_id"],
        user_id=data["user_id"],
    )
    log.info("Dispatched provision_lab", instance_id=data["instance_id"])


# Registry mapping topic → handler
TOPIC_HANDLERS: dict[str, Any] = {
    "submission.created": handle_submission_created,
    "submission.completed": handle_submission_completed,
    "notification.send": handle_notification_send,
    "payment.completed": handle_payment_completed,
    "contest.started": handle_contest_started,
    "lab.started": handle_lab_started,
}
