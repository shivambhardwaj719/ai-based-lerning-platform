"""Notification tasks: email, push, in-app notifications."""
from __future__ import annotations

import structlog
from workers.celery_app import celery_app

log = structlog.get_logger()


@celery_app.task(name="workers.tasks.notification_tasks.send_email", queue="notifications")
def send_email_task(to: str, subject: str, template: str, context: dict) -> None:
    import asyncio
    from utils.email import EmailService
    async def _send():
        svc = EmailService()
        await svc.send_template(to=to, subject=subject, template=template, context=context)
    asyncio.get_event_loop().run_until_complete(_send())


@celery_app.task(name="workers.tasks.notification_tasks.send_weekly_digest", queue="notifications")
def send_weekly_digest() -> None:
    log.info("Sending weekly digest emails")


@celery_app.task(name="workers.tasks.notification_tasks.send_contest_reminder", queue="notifications")
def send_contest_reminder(contest_id: str) -> None:
    log.info("Sending contest reminder", contest_id=contest_id)
