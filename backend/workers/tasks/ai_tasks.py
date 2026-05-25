"""
AI background tasks: async problem generation, roadmap updates,
AI-based evaluation, embedding indexing, recommendation pre-computation.
"""
from __future__ import annotations

import asyncio
import uuid

import structlog

from workers.celery_app import celery_app

log = structlog.get_logger()


def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)


@celery_app.task(
    name="workers.tasks.ai_tasks.generate_ai_feedback",
    queue="ai",
    max_retries=2,
)
def generate_ai_feedback(submission_id: str) -> dict:
    """Generate AI-powered feedback for a submission using code review agent."""
    log.info("Generating AI feedback", submission_id=submission_id)

    async def _generate():
        from core.database import database_manager
        from repositories.problem_repository import SubmissionRepository

        async with database_manager.session() as db:
            sub_repo = SubmissionRepository(db)
            submission = await sub_repo.get_by_id(uuid.UUID(submission_id))
            if not submission:
                return {"error": "Submission not found"}

            from ai.agents.code_review_agent import CodeReviewAgent
            agent = CodeReviewAgent()
            review = await agent.review(
                code=submission.code,
                language=submission.language,
                focus_areas=["correctness", "efficiency", "style"],
            )

            await sub_repo.update(
                submission.id,
                ai_feedback=review.get("feedback", ""),
                ai_score=review.get("overall_score", 0.0),
            )
            log.info("AI feedback generated", submission_id=submission_id, score=review.get("overall_score"))
            return review

    return run_async(_generate())


@celery_app.task(
    name="workers.tasks.ai_tasks.index_study_material",
    queue="ai",
)
def index_study_material(material_id: str) -> None:
    """Index a study material into Qdrant vector database for RAG."""
    log.info("Indexing study material", material_id=material_id)

    async def _index():
        from core.database import database_manager
        from models.ai_conversation import StudyMaterial
        from repositories.base import BaseRepository

        async with database_manager.session() as db:
            repo = BaseRepository(StudyMaterial, db)
            material = await repo.get_by_id(uuid.UUID(material_id))
            if not material:
                return

            from ai.rag.retriever import KnowledgeRetriever
            retriever = KnowledgeRetriever()
            await retriever.index_document(
                doc_id=material_id,
                content=material.content,
                title=material.title,
                source="study_material",
                metadata={
                    "topic": material.topic,
                    "subtopic": material.subtopic,
                    "difficulty": material.difficulty_level,
                    "tags": material.tags or [],
                },
            )
            log.info("Study material indexed", material_id=material_id)

    run_async(_index())


@celery_app.task(
    name="workers.tasks.ai_tasks.bulk_index_problems",
    queue="ai",
)
def bulk_index_problems() -> None:
    """Bulk index all published problems into Elasticsearch and Qdrant."""
    log.info("Bulk indexing problems")

    async def _bulk_index():
        from core.database import database_manager
        from core.elasticsearch import es_manager

        async with database_manager.session() as db:
            from repositories.problem_repository import ProblemRepository
            repo = ProblemRepository(db)
            problems, _ = await repo.get_published_problems(limit=10000, offset=0)

            docs = [
                {
                    "id": str(p.id),
                    "title": p.title,
                    "description": p.description[:500],
                    "difficulty": p.difficulty,
                    "tags": p.tags or [],
                    "problem_type": p.problem_type,
                    "acceptance_rate": p.acceptance_rate,
                }
                for p in problems
            ]
            await es_manager.bulk_index("problems", docs)
            log.info("Problems indexed", count=len(docs))

    run_async(_bulk_index())


@celery_app.task(
    name="workers.tasks.ai_tasks.generate_adaptive_recommendations",
    queue="ai",
)
def generate_adaptive_recommendations(user_id: str) -> dict:
    """Generate personalized problem recommendations for a user."""
    log.info("Generating recommendations", user_id=user_id)

    async def _recommend():
        from core.database import database_manager

        async with database_manager.session() as db:
            from repositories.user_repository import UserRepository
            from repositories.problem_repository import SubmissionRepository, ProblemRepository

            user_repo = UserRepository(db)
            user = await user_repo.get_with_profile(uuid.UUID(user_id))
            if not user:
                return {"error": "User not found"}

            sub_repo = SubmissionRepository(db)
            recent_subs = await sub_repo.get_user_submissions(
                uuid.UUID(user_id), limit=20
            )

            # Simple collaborative filtering: recommend unsolved problems
            # matching user skill tags
            prob_repo = ProblemRepository(db)
            skill_tags = user.skills or []
            if not skill_tags:
                skill_tags = ["array", "string"]

            recommended, _ = await prob_repo.get_published_problems(
                tags=skill_tags, limit=10
            )

            solved_ids = set()
            for sub in recent_subs:
                from models.problem import SubmissionStatus
                if sub.status == SubmissionStatus.ACCEPTED:
                    solved_ids.add(str(sub.problem_id))

            filtered = [p for p in recommended if str(p.id) not in solved_ids][:5]

            # Cache recommendations in Redis
            from core.redis import redis_manager
            recs = [{"id": str(p.id), "title": p.title, "difficulty": p.difficulty} for p in filtered]
            await redis_manager.set(f"recommendations:{user_id}", recs, ttl=3600)

            return {"user_id": user_id, "recommendations": recs}

    return run_async(_recommend())


@celery_app.task(
    name="workers.tasks.ai_tasks.update_roadmap_progress",
    queue="ai",
)
def update_roadmap_progress(user_id: str) -> None:
    """Recalculate roadmap progress based on recent submissions."""
    log.info("Updating roadmap progress", user_id=user_id)

    async def _update():
        from core.database import database_manager

        async with database_manager.session() as db:
            from repositories.ai_repository import RoadmapRepository
            repo = RoadmapRepository(db)
            roadmaps = await repo.get_user_roadmaps(uuid.UUID(user_id))

            for roadmap in roadmaps:
                nodes = roadmap.nodes or []
                if not nodes:
                    continue
                completed = sum(1 for n in nodes if n.get("completed", False))
                progress = (completed / len(nodes) * 100) if nodes else 0.0
                await repo.update(roadmap.id, progress_percentage=progress)

    run_async(_update())
