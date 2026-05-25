"""Payments API: subscriptions, checkout, webhooks."""
from __future__ import annotations

import stripe
from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import CurrentUser
from core.config import settings
from core.database import get_db
from core.exceptions import PaymentError

router = APIRouter(prefix="/payments", tags=["Payments"])
stripe.api_key = settings.STRIPE_SECRET_KEY


@router.get("/plans")
async def list_plans(db: AsyncSession = Depends(get_db)) -> dict:
    from repositories.payment_repository import PlanRepository
    repo = PlanRepository(db)
    plans = await repo.get_active_plans()
    return {"plans": plans}


@router.post("/subscribe")
async def create_subscription(
    body: dict,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    plan_id = body.get("plan_id")
    billing_cycle = body.get("billing_cycle", "monthly")

    from repositories.payment_repository import PlanRepository
    plan_repo = PlanRepository(db)
    plan = await plan_repo.get_by_id(plan_id)
    if not plan:
        from core.exceptions import NotFoundError
        raise NotFoundError("Plan")

    price_id = plan.stripe_price_id_monthly if billing_cycle == "monthly" else plan.stripe_price_id_yearly

    try:
        checkout = stripe.checkout.Session.create(
            customer_email=current_user.email,
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=f"{settings.CORS_ORIGINS[0]}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.CORS_ORIGINS[0]}/subscription/cancel",
            metadata={"user_id": str(current_user.id), "plan_id": str(plan_id)},
        )
        return {"checkout_url": checkout.url, "session_id": checkout.id}
    except stripe.StripeError as e:
        raise PaymentError(str(e))


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(alias="stripe-signature"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET)
    except ValueError:
        raise PaymentError("Invalid payload")
    except stripe.SignatureVerificationError:
        raise PaymentError("Invalid signature")

    from workers.tasks.payment_tasks import process_stripe_webhook
    process_stripe_webhook.delay(event)
    return {"received": True}


@router.get("/subscription")
async def get_subscription(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    from repositories.payment_repository import SubscriptionRepository
    repo = SubscriptionRepository(db)
    sub = await repo.get_active_subscription(current_user.id)
    return {"subscription": sub}


@router.post("/subscription/cancel")
async def cancel_subscription(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    from repositories.payment_repository import SubscriptionRepository
    repo = SubscriptionRepository(db)
    sub = await repo.get_active_subscription(current_user.id)
    if not sub:
        raise PaymentError("No active subscription")

    if sub.stripe_subscription_id:
        stripe.Subscription.modify(sub.stripe_subscription_id, cancel_at_period_end=True)

    await repo.update(sub.id, cancel_at_period_end=True)
    return {"message": "Subscription will be cancelled at the end of billing period"}
