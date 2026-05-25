"""Contest and ContestParticipant repositories."""
from __future__ import annotations

import uuid
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.contest import Contest, ContestParticipant
from repositories.base import BaseRepository


class ContestRepository(BaseRepository[Contest]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Contest, db)

    async def get_by_slug(self, slug: str) -> Contest | None:
        return await self.get_by_field("slug", slug)

    async def get_contests(self, status: str | None = None, limit: int = 20, offset: int = 0) -> tuple[list, int]:
        filters = []
        if status:
            filters.append(Contest.status == status)
        contests = await self.get_all(filters=filters or None, limit=limit, offset=offset)
        total = await self.count(filters=filters or None)
        return contests, total


class ContestParticipantRepository(BaseRepository[ContestParticipant]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(ContestParticipant, db)

    async def is_registered(self, contest_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        stmt = select(func.count()).select_from(ContestParticipant).where(
            and_(ContestParticipant.contest_id == contest_id, ContestParticipant.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() > 0

    async def get_leaderboard(self, contest_id: uuid.UUID, limit: int = 50, offset: int = 0) -> tuple[list, int]:
        filters = [ContestParticipant.contest_id == contest_id]
        entries = await self.get_all(
            filters=filters,
            order_by=[ContestParticipant.total_score.desc(), ContestParticipant.penalty_time.asc()],
            limit=limit, offset=offset,
        )
        total = await self.count(filters=filters)
        return entries, total
