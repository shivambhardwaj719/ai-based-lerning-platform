"""
AI Service API: chat, roadmap, problem generation, code review, interviews.
Supports both streaming and non-streaming responses.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import CurrentUser, VerifiedUser
from core.database import get_db
from core.exceptions import NotFoundError, ServiceUnavailableError
from schemas.ai import (
    ChatRequest,
    ChatResponse,
    CodeReviewRequest,
    CodeReviewResponse,
    ConversationDetailResponse,
    ConversationResponse,
    InterviewSessionRequest,
    InterviewSessionResponse,
    ProblemGenerateRequest,
    RoadmapGenerateRequest,
    RoadmapResponse,
)

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/chat")
async def chat(
    body: ChatRequest,
    current_user: VerifiedUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Chat with AI mentor. Supports streaming via SSE.
    Creates or continues an existing conversation.
    """
    from ai.agents.mentor_agent import MentorAgent

    agent = MentorAgent(user_id=current_user.id, db=db)

    if body.stream:
        async def event_stream():
            async for chunk in agent.stream_response(
                message=body.message,
                conversation_id=body.conversation_id,
                conversation_type=body.conversation_type,
                context=body.context,
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    response = await agent.get_response(
        message=body.message,
        conversation_id=body.conversation_id,
        conversation_type=body.conversation_type,
        context=body.context,
    )
    return ChatResponse(**response)


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
) -> list[ConversationResponse]:
    from repositories.ai_repository import ConversationRepository
    repo = ConversationRepository(db)
    conversations = await repo.get_user_conversations(
        current_user.id, limit=page_size, offset=(page - 1) * page_size
    )
    return [ConversationResponse.model_validate(c) for c in conversations]


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> ConversationDetailResponse:
    from repositories.ai_repository import ConversationRepository
    repo = ConversationRepository(db)
    conv = await repo.get_with_messages(conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise NotFoundError("Conversation")
    return ConversationDetailResponse.model_validate(conv)


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    from repositories.ai_repository import ConversationRepository
    repo = ConversationRepository(db)
    conv = await repo.get_by_id(conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise NotFoundError("Conversation")
    await repo.delete(conversation_id)
    return {"message": "Conversation deleted"}


@router.post("/roadmap/generate", response_model=RoadmapResponse)
async def generate_roadmap(
    body: RoadmapGenerateRequest,
    current_user: VerifiedUser,
    db: AsyncSession = Depends(get_db),
) -> RoadmapResponse:
    from ai.agents.roadmap_agent import RoadmapAgent
    agent = RoadmapAgent(user_id=current_user.id, db=db)
    roadmap = await agent.generate(
        goal=body.goal,
        target_role=body.target_role,
        current_skills=body.current_skills,
        experience_level=body.experience_level,
        available_hours_per_week=body.available_hours_per_week,
        timeline_weeks=body.timeline_weeks,
    )
    return RoadmapResponse.model_validate(roadmap)


@router.get("/roadmaps", response_model=list[RoadmapResponse])
async def list_roadmaps(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> list[RoadmapResponse]:
    from repositories.ai_repository import RoadmapRepository
    repo = RoadmapRepository(db)
    roadmaps = await repo.get_user_roadmaps(current_user.id)
    return [RoadmapResponse.model_validate(r) for r in roadmaps]


@router.post("/code-review", response_model=CodeReviewResponse)
async def review_code(
    body: CodeReviewRequest,
    current_user: VerifiedUser,
) -> CodeReviewResponse:
    from ai.agents.code_review_agent import CodeReviewAgent
    agent = CodeReviewAgent()
    review = await agent.review(
        code=body.code,
        language=body.language,
        problem_context=body.problem_context,
        focus_areas=body.focus_areas,
    )
    return CodeReviewResponse(**review)


@router.post("/problems/generate")
async def generate_problem(
    body: ProblemGenerateRequest,
    current_user: VerifiedUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    from ai.agents.problem_generator import ProblemGeneratorAgent
    agent = ProblemGeneratorAgent(db=db)
    problems = await agent.generate(
        topic=body.topic,
        difficulty=body.difficulty,
        problem_type=body.problem_type,
        tags=body.tags,
        count=body.count,
    )
    return {"problems": problems, "count": len(problems)}


@router.post("/interview/start", response_model=InterviewSessionResponse)
async def start_interview(
    body: InterviewSessionRequest,
    current_user: VerifiedUser,
    db: AsyncSession = Depends(get_db),
) -> InterviewSessionResponse:
    from ai.agents.interview_agent import InterviewAgent
    agent = InterviewAgent(user_id=current_user.id, db=db)
    session = await agent.start_session(
        interview_type=body.interview_type,
        role=body.role,
        experience_level=body.experience_level,
        topics=body.topics,
        duration_minutes=body.duration_minutes,
    )
    return InterviewSessionResponse(**session)


@router.post("/interview/{session_id}/answer")
async def answer_interview_question(
    session_id: uuid.UUID,
    answer: dict,
    current_user: CurrentUser,
) -> dict:
    from ai.agents.interview_agent import InterviewAgent
    agent = InterviewAgent(user_id=current_user.id)
    result = await agent.evaluate_answer(
        session_id=session_id,
        answer=answer.get("answer", ""),
    )
    return result


@router.post("/debug")
async def debug_code(
    body: dict,
    current_user: VerifiedUser,
) -> dict:
    """AI-powered debugging assistant."""
    from ai.agents.debug_agent import DebugAgent
    agent = DebugAgent()
    result = await agent.debug(
        code=body.get("code", ""),
        language=body.get("language", "python"),
        error=body.get("error", ""),
        context=body.get("context"),
    )
    return result
