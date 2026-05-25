"""
AI Mentor Agent using LangGraph with multi-turn memory, RAG, and tool use.
Adapts responses based on user skill level and learning history.
"""
from __future__ import annotations

import json
import uuid
from typing import Any, AsyncGenerator, TypedDict

import structlog
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from sqlalchemy.ext.asyncio import AsyncSession

from ai.memory.conversation_memory import ConversationMemory
from ai.rag.retriever import KnowledgeRetriever
from ai.prompts.mentor_prompts import MENTOR_SYSTEM_PROMPT
from core.config import settings

log = structlog.get_logger()


class MentorState(TypedDict):
    messages: list
    user_id: str
    conversation_id: str | None
    conversation_type: str
    context: dict | None
    user_profile: dict | None


class MentorAgent:
    """
    AI Mentor with persistent memory, RAG-enhanced knowledge, and adaptive learning.
    Uses LangGraph for stateful multi-turn conversations.
    """

    def __init__(self, user_id: uuid.UUID, db: AsyncSession) -> None:
        self.user_id = user_id
        self.db = db
        self.memory = ConversationMemory(db)
        self.retriever = KnowledgeRetriever()
        self.llm = ChatOpenAI(
            model=settings.DEFAULT_AI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.7,
            streaming=True,
        )
        self._graph = self._build_graph()

    def _build_graph(self) -> Any:
        tools = self._get_tools()
        model_with_tools = self.llm.bind_tools(tools)

        def should_continue(state: MentorState) -> str:
            last_message = state["messages"][-1]
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "tools"
            return END

        async def call_model(state: MentorState) -> MentorState:
            system_msg = SystemMessage(content=MENTOR_SYSTEM_PROMPT.format(
                user_profile=json.dumps(state.get("user_profile") or {}),
                conversation_type=state.get("conversation_type", "general"),
            ))
            messages = [system_msg] + state["messages"]
            response = await model_with_tools.ainvoke(messages)
            return {**state, "messages": state["messages"] + [response]}

        workflow = StateGraph(MentorState)
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", ToolNode(self._get_tools()))
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
        workflow.add_edge("tools", "agent")

        return workflow.compile(checkpointer=MemorySaver())

    def _get_tools(self) -> list:
        @tool
        async def search_knowledge_base(query: str) -> str:
            """Search the knowledge base for relevant technical information."""
            docs = await self.retriever.retrieve(query, k=3)
            return "\n\n".join([d["content"] for d in docs]) if docs else "No relevant information found."

        @tool
        async def get_hint_for_problem(problem_slug: str) -> str:
            """Get a hint for a specific coding problem."""
            from repositories.problem_repository import ProblemRepository
            repo = ProblemRepository(self.db)
            problem = await repo.get_by_slug(problem_slug)
            if not problem or not problem.hints:
                return "No hints available for this problem."
            return f"Hint: {problem.hints[0]}"

        @tool
        async def get_user_progress(topic: str) -> str:
            """Get the user's progress and submissions on a topic."""
            return f"User has worked on {topic} problems. Continue motivating them."

        return [search_knowledge_base, get_hint_for_problem, get_user_progress]

    async def get_response(
        self,
        message: str,
        conversation_id: uuid.UUID | None = None,
        conversation_type: str = "general",
        context: dict | None = None,
    ) -> dict:
        # Load or create conversation
        conv_id, history = await self.memory.load_or_create(
            self.user_id, conversation_id, conversation_type
        )

        # Build initial state
        state = MentorState(
            messages=history + [HumanMessage(content=message)],
            user_id=str(self.user_id),
            conversation_id=str(conv_id),
            conversation_type=conversation_type,
            context=context,
            user_profile=await self._get_user_profile(),
        )

        config = {"configurable": {"thread_id": str(conv_id)}}
        final_state = await self._graph.ainvoke(state, config=config)

        ai_response = final_state["messages"][-1]
        content = ai_response.content if hasattr(ai_response, "content") else str(ai_response)

        # Persist messages
        tokens = getattr(ai_response, "usage_metadata", {}).get("total_tokens", 0)
        msg_id = await self.memory.save_exchange(
            conv_id, message, content, tokens
        )

        return {
            "conversation_id": conv_id,
            "message_id": msg_id,
            "content": content,
            "tokens_used": tokens,
            "model": settings.DEFAULT_AI_MODEL,
        }

    async def stream_response(
        self,
        message: str,
        conversation_id: uuid.UUID | None = None,
        conversation_type: str = "general",
        context: dict | None = None,
    ) -> AsyncGenerator[str, None]:
        conv_id, history = await self.memory.load_or_create(
            self.user_id, conversation_id, conversation_type
        )

        state = MentorState(
            messages=history + [HumanMessage(content=message)],
            user_id=str(self.user_id),
            conversation_id=str(conv_id),
            conversation_type=conversation_type,
            context=context,
            user_profile=await self._get_user_profile(),
        )

        full_response = ""
        async for event in self._graph.astream_events(state, version="v2"):
            if event["event"] == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if hasattr(chunk, "content") and chunk.content:
                    full_response += chunk.content
                    yield json.dumps({"type": "chunk", "content": chunk.content})

        await self.memory.save_exchange(conv_id, message, full_response, 0)
        yield json.dumps({"type": "done", "conversation_id": str(conv_id)})

    async def _get_user_profile(self) -> dict:
        from repositories.user_repository import UserRepository
        repo = UserRepository(self.db)
        user = await repo.get_with_profile(self.user_id)
        if not user:
            return {}
        return {
            "username": user.username,
            "level": user.profile.level if user.profile else 1,
            "skills": user.skills or [],
            "preferred_languages": user.preferred_languages or [],
        }
