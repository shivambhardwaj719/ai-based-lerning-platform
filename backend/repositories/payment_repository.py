"""Payment, Plan, and Subscription repositories."""
from __future__ import annotations

import uuid
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.payment import Payment, Plan, Subscription, SubscriptionStatus
from repositories.base import BaseRepository


class PlanRepository(BaseRepository[Plan]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Plan, db)

    async def get_active_plans(self) -> list[Plan]:
        return await self.get_all(filters=[Plan.is_active == True])


class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Subscription, db)

    async def get_active_subscription(self, user_id: uuid.UUID) -> Subscription | None:
        stmt = select(Subscription).where(
            and_(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.ACTIVE,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Payment, db)
