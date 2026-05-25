"""Pydantic v2 schemas for Payment and Subscription endpoints."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class PlanResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    price_monthly: float
    price_yearly: float
    features: list[str]
    max_submissions_per_day: int
    has_ai_mentor: bool
    has_lab_access: bool
    has_contest_access: bool
    is_active: bool

    model_config = {"from_attributes": True}


class CreateCheckoutSession(BaseModel):
    plan_id: uuid.UUID
    billing_cycle: str = Field(..., pattern="^(monthly|yearly)$")
    success_url: str
    cancel_url: str


class CheckoutSessionResponse(BaseModel):
    session_id: str
    checkout_url: str
    plan_id: uuid.UUID
    amount: float
    currency: str


class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    plan: PlanResponse
    status: str
    billing_cycle: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CancelSubscriptionRequest(BaseModel):
    cancel_at_period_end: bool = True
    reason: str | None = None


class PaymentHistoryItem(BaseModel):
    id: uuid.UUID
    amount: float
    currency: str
    status: str
    description: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PaymentHistoryResponse(BaseModel):
    payments: list[PaymentHistoryItem]
    total: int


class WebhookEvent(BaseModel):
    id: str
    type: str
    data: dict


class UsageResponse(BaseModel):
    submissions_today: int
    submissions_limit: int
    ai_queries_today: int
    ai_queries_limit: int
    active_labs: int
    labs_limit: int
