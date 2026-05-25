"""
Celery application configuration with Redis broker and result backend.
Supports scheduled tasks (celery-redbeat) and task routing.
"""
from __future__ import annotations

from celery import Celery
from celery.schedules import crontab
from kombu import Queue

from core.config import settings

celery_app = Celery(
    "ai_learning_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "workers.tasks.submission_tasks",
        "workers.tasks.notification_tasks",
        "workers.tasks.ai_tasks",
        "workers.tasks.analytics_tasks",
        "workers.tasks.payment_tasks",
        "workers.tasks.lab_tasks",
        "workers.tasks.maintenance_tasks",
    ],
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Task settings
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,

    # Result expiry
    result_expires=3600,

    # Routing
    task_queues=(
        Queue("default", routing_key="default"),
        Queue("submissions", routing_key="submissions"),
        Queue("notifications", routing_key="notifications"),
        Queue("ai", routing_key="ai"),
        Queue("analytics", routing_key="analytics"),
        Queue("payments", routing_key="payments"),
        Queue("labs", routing_key="labs"),
        Queue("maintenance", routing_key="maintenance"),
    ),
    task_default_queue="default",
    task_routes={
        "workers.tasks.submission_tasks.*": {"queue": "submissions"},
        "workers.tasks.notification_tasks.*": {"queue": "notifications"},
        "workers.tasks.ai_tasks.*": {"queue": "ai"},
        "workers.tasks.analytics_tasks.*": {"queue": "analytics"},
        "workers.tasks.payment_tasks.*": {"queue": "payments"},
        "workers.tasks.lab_tasks.*": {"queue": "labs"},
        "workers.tasks.maintenance_tasks.*": {"queue": "maintenance"},
    },

    # Beat schedule (cron jobs)
    beat_schedule={
        "update-acceptance-rates": {
            "task": "workers.tasks.maintenance_tasks.update_acceptance_rates",
            "schedule": crontab(minute="*/30"),
        },
        "expire-lab-instances": {
            "task": "workers.tasks.lab_tasks.expire_lab_instances",
            "schedule": crontab(minute="*/5"),
        },
        "update-leaderboard": {
            "task": "workers.tasks.analytics_tasks.update_global_leaderboard",
            "schedule": crontab(minute="*/15"),
        },
        "cleanup-expired-sessions": {
            "task": "workers.tasks.maintenance_tasks.cleanup_expired_sessions",
            "schedule": crontab(hour="*/6"),
        },
        "send-weekly-digest": {
            "task": "workers.tasks.notification_tasks.send_weekly_digest",
            "schedule": crontab(day_of_week="monday", hour="9", minute="0"),
        },
        "check-contest-status": {
            "task": "workers.tasks.maintenance_tasks.check_contest_status",
            "schedule": crontab(minute="*"),
        },
    },
)
