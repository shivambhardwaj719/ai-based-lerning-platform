"""Payment processing tasks: webhook handling, subscription updates."""
from __future__ import annotations

import structlog
from workers.celery_app import celery_app

log = structlog.get_logger()


@celery_app.task(name="workers.tasks.payment_tasks.process_stripe_webhook", queue="payments")
def process_stripe_webhook(event: dict) -> None:
    import asyncio
    event_type = event.get("type", "")
    log.info("Processing Stripe webhook", event_type=event_type)

    async def _process():
        from core.database import database_manager
        async with database_manager.session() as db:
            if event_type == "checkout.session.completed":
                await _handle_checkout_completed(db, event["data"]["object"])
            elif event_type == "customer.subscription.updated":
                await _handle_subscription_updated(db, event["data"]["object"])
            elif event_type == "customer.subscription.deleted":
                await _handle_subscription_deleted(db, event["data"]["object"])
            elif event_type == "invoice.payment_succeeded":
                await _handle_payment_succeeded(db, event["data"]["object"])
            elif event_type == "invoice.payment_failed":
                await _handle_payment_failed(db, event["data"]["object"])

    asyncio.get_event_loop().run_until_complete(_process())


async def _handle_checkout_completed(db, session_obj: dict) -> None:
    import uuid
    from models.user import SubscriptionTier
    from repositories.user_repository import UserRepository
    meta = session_obj.get("metadata", {})
    user_id = meta.get("user_id")
    plan_id = meta.get("plan_id")
    if not user_id:
        return

    from sqlalchemy import text
    from datetime import UTC, datetime, timedelta
    await db.execute(text("""
        INSERT INTO subscriptions (id, user_id, plan_id, status, billing_cycle,
            current_period_start, current_period_end, stripe_subscription_id)
        VALUES (gen_random_uuid(), :uid, :pid, 'active', 'monthly', NOW(), NOW() + INTERVAL '30 days', :sid)
    """), {"uid": user_id, "pid": plan_id, "sid": session_obj.get("subscription", "")})

    user_repo = UserRepository(db)
    await user_repo.update(uuid.UUID(user_id), subscription_tier=SubscriptionTier.PRO)
    log.info("Subscription activated", user_id=user_id)


async def _handle_subscription_updated(db, sub_obj: dict) -> None:
    log.info("Subscription updated", sub_id=sub_obj.get("id"))


async def _handle_subscription_deleted(db, sub_obj: dict) -> None:
    from sqlalchemy import text
    await db.execute(text(
        "UPDATE subscriptions SET status = 'cancelled' WHERE stripe_subscription_id = :sid"
    ), {"sid": sub_obj.get("id")})


async def _handle_payment_succeeded(db, invoice: dict) -> None:
    log.info("Payment succeeded", invoice_id=invoice.get("id"))


async def _handle_payment_failed(db, invoice: dict) -> None:
    log.warning("Payment failed", invoice_id=invoice.get("id"))
