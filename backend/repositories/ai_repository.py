"""AI conversation and roadmap repositories."""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.ai_conversation import AIConversation, AIMessage, Roadmap
from repositories.base import BaseRepository


class ConversationRepository(BaseRepository[AIConversation]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(AIConversation, db)

    async def get_user_conversations(self, user_id: uuid.UUID, limit: int = 20, offset: int = 0) -> list[AIConversation]:
        stmt = (
            select(AIConversation)
            .where(AIConversation.user_id == user_id)
            .order_by(AIConversation.updated_at.desc())
            .limit(limit).offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_with_messages(self, conv_id: uuid.UUID) -> AIConversation | None:
        stmt = (
            select(AIConversation)
            .where(AIConversation.id == conv_id)
            .options(selectinload(AIConversation.messages))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class MessageRepository(BaseRepository[AIMessage]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(AIMessage, db)

    async def get_conversation_messages(self, conv_id: uuid.UUID) -> list[AIMessage]:
        stmt = (
            select(AIMessage)
            .where(AIMessage.conversation_id == conv_id)
            .order_by(AIMessage.order_index)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_next_index(self, conv_id: uuid.UUID) -> int:
        from sqlalchemy import func
        stmt = select(func.count()).select_from(AIMessage).where(AIMessage.conversation_id == conv_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()


class RoadmapRepository(BaseRepository[Roadmap]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Roadmap, db)

    async def get_user_roadmaps(self, user_id: uuid.UUID) -> list[Roadmap]:
        return await self.get_all(filters=[Roadmap.user_id == user_id, Roadmap.is_active == True])
