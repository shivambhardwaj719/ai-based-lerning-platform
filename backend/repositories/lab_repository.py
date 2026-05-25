"""Lab and LabInstance repositories."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from models.lab import Lab, LabInstance
from repositories.base import BaseRepository


class LabRepository(BaseRepository[Lab]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Lab, db)

    async def get_by_slug(self, slug: str) -> Lab | None:
        return await self.get_by_field("slug", slug)

    async def get_published_labs(self, lab_type: str | None = None, difficulty: str | None = None,
                                  limit: int = 20, offset: int = 0) -> tuple[list, int]:
        filters = [Lab.is_published == True]
        if lab_type:
            filters.append(Lab.lab_type == lab_type)
        if difficulty:
            filters.append(Lab.difficulty == difficulty)
        labs = await self.get_all(filters=filters, limit=limit, offset=offset)
        total = await self.count(filters=filters)
        return labs, total


class LabInstanceRepository(BaseRepository[LabInstance]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(LabInstance, db)
