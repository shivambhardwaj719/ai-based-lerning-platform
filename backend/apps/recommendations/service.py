"""Recommendation service — personalized problem and content suggestions."""
from __future__ import annotations

import uuid
from typing import Any

import structlog

log = structlog.get_logger()


class RecommendationService:
    """Generate personalized problem recommendations using skill-based filtering."""

    def __init__(self, db):
        self.db = db

    async def get_recommendations(self, user_id: uuid.UUID, limit: int = 10) -> list[dict[str, Any]]:
        """Return personalized problem recommendations, cached in Redis."""
        from core.redis import redis_manager

        cache_key = f"recommendations:{user_id}"
        cached = await redis_manager.get(cache_key)
        if cached:
            return cached[:limit]

        recs = await self._compute_recommendations(user_id, limit)
        await redis_manager.set(cache_key, recs, ttl=3600)
        return recs

    async def _compute_recommendations(self, user_id: uuid.UUID, limit: int) -> list[dict]:
        """Multi-strategy recommendation: skill-tag + difficulty progression."""
        from repositories.problem_repository import ProblemRepository, SubmissionRepository
        from repositories.user_repository import UserRepository
        from sqlalchemy import text

        user_repo = UserRepository(self.db)
        user = await user_repo.get_with_profile(user_id)
        if not user:
            return []

        # Get recently solved problem IDs
        sub_repo = SubmissionRepository(self.db)
        recent = await sub_repo.get_user_submissions(user_id, limit=100)
        solved_ids = {str(s.problem_id) for s in recent if s.status.value == "accepted"}

        profile = user.profile
        target_difficulty = self._next_difficulty(profile.problems_solved if profile else 0)
        skill_tags = user.skills or ["array", "string"]

        # Skill-tag matching with difficulty progression
        prob_repo = ProblemRepository(self.db)
        candidates, _ = await prob_repo.get_published_problems(
            tags=skill_tags,
            difficulty=target_difficulty,
            limit=limit * 3,
        )

        # Filter already solved
        unsolved = [p for p in candidates if str(p.id) not in solved_ids]

        # Sort by acceptance rate (prefer ~50-70% acceptance as optimal challenge)
        def optimal_score(p):
            rate = p.acceptance_rate or 50.0
            return abs(rate - 60)

        unsolved.sort(key=optimal_score)

        return [
            {
                "id": str(p.id),
                "title": p.title,
                "difficulty": p.difficulty,
                "tags": p.tags or [],
                "acceptance_rate": p.acceptance_rate,
                "reason": f"Matches your {skill_tags[0]} skill" if skill_tags else "Popular problem",
            }
            for p in unsolved[:limit]
        ]

    def _next_difficulty(self, problems_solved: int) -> str:
        """Map solved count to recommended difficulty band."""
        if problems_solved < 10:
            return "easy"
        if problems_solved < 50:
            return "medium"
        return "hard"

    async def invalidate_cache(self, user_id: uuid.UUID) -> None:
        from core.redis import redis_manager
        await redis_manager.delete(f"recommendations:{user_id}")
