"""
Generic async repository implementing the repository pattern.
Provides CRUD operations with type safety via generics.
"""
from __future__ import annotations

import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import Select, func, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


class BaseRepository(Generic[ModelT]):
    """Generic repository with full CRUD support."""

    def __init__(self, model: type[ModelT], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get_by_id(self, id_: uuid.UUID) -> ModelT | None:
        result = await self.session.get(self.model, id_)
        return result

    async def get_by_field(self, field: str, value: Any) -> ModelT | None:
        stmt = select(self.model).where(getattr(self.model, field) == value)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
        filters: list | None = None,
        order_by: list | None = None,
    ) -> list[ModelT]:
        stmt = select(self.model)
        if filters:
            stmt = stmt.where(*filters)
        if order_by:
            stmt = stmt.order_by(*order_by)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, filters: list | None = None) -> int:
        stmt = select(func.count()).select_from(self.model)
        if filters:
            stmt = stmt.where(*filters)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def create(self, **kwargs: Any) -> ModelT:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, id_: uuid.UUID, **kwargs: Any) -> ModelT | None:
        stmt = (
            update(self.model)
            .where(self.model.id == id_)
            .values(**kwargs)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, id_: uuid.UUID) -> bool:
        stmt = delete(self.model).where(self.model.id == id_)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def bulk_create(self, items: list[dict]) -> list[ModelT]:
        instances = [self.model(**item) for item in items]
        self.session.add_all(instances)
        await self.session.flush()
        return instances

    def _build_select(self, *options: Any) -> Select:
        return select(self.model).options(*options)
