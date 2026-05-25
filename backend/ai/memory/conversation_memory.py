"""Persistent conversation memory backed by PostgreSQL."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from sqlalchemy.ext.asyncio import AsyncSession


class ConversationMemory:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def load_or_create(
        self,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID | None,
        conversation_type: str,
    ) -> tuple[uuid.UUID, list]:
        from repositories.ai_repository import ConversationRepository, MessageRepository
        conv_repo = ConversationRepository(self.db)

        if conversation_id:
            conv = await conv_repo.get_by_id(conversation_id)
            if conv and conv.user_id == user_id:
                msg_repo = MessageRepository(self.db)
                messages = await msg_repo.get_conversation_messages(conversation_id)
                history = []
                for m in messages:
                    if m.role == "user":
                        history.append(HumanMessage(content=m.content))
                    elif m.role == "assistant":
                        history.append(AIMessage(content=m.content))
                return conversation_id, history

        # Create new conversation
        conv = await conv_repo.create(
            user_id=user_id,
            conversation_type=conversation_type,
            title=f"New {conversation_type} session",
        )
        return conv.id, []

    async def save_exchange(
        self,
        conversation_id: uuid.UUID,
        user_message: str,
        ai_response: str,
        tokens_used: int,
    ) -> uuid.UUID:
        from repositories.ai_repository import MessageRepository, ConversationRepository
        msg_repo = MessageRepository(self.db)

        await msg_repo.create(
            conversation_id=conversation_id,
            role="user",
            content=user_message,
            order_index=await msg_repo.get_next_index(conversation_id),
        )
        ai_msg = await msg_repo.create(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response,
            tokens_used=tokens_used,
            order_index=await msg_repo.get_next_index(conversation_id),
        )

        # Update conversation token count
        conv_repo = ConversationRepository(self.db)
        from sqlalchemy import text
        await self.db.execute(
            text("UPDATE ai_conversations SET total_tokens_used = total_tokens_used + :t WHERE id = :id"),
            {"t": tokens_used, "id": conversation_id},
        )

        return ai_msg.id
