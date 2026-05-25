"""Analytics service — platform metrics, user activity, trend analysis."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import structlog

log = structlog.get_logger()


class AnalyticsService:
    """Compute and cache analytics metrics for the platform."""

    def __init__(self, db):
        self.db = db

    async def get_platform_stats(self) -> dict:
        """Return key platform KPIs from DB + Redis cache."""
        from core.redis import redis_manager
        from sqlalchemy import text

        cached = await redis_manager.get("analytics:platform_stats")
        if cached:
            return cached

        result = {}
        queries = {
            "total_users": "SELECT COUNT(*) FROM users",
            "active_today": "SELECT COUNT(DISTINCT user_id) FROM audit_logs WHERE created_at >= NOW() - INTERVAL '24 hours' AND success = true",
            "total_submissions": "SELECT COUNT(*) FROM submissions",
            "accepted_submissions": "SELECT COUNT(*) FROM submissions WHERE status = 'accepted'",
            "total_problems": "SELECT COUNT(*) FROM problems WHERE is_published = true",
            "total_contests": "SELECT COUNT(*) FROM contests",
        }

        for key, query in queries.items():
            val = (await self.db.execute(text(query))).scalar_one_or_none() or 0
            result[key] = val

        total = result["total_submissions"]
        accepted = result["accepted_submissions"]
        result["global_acceptance_rate"] = round(accepted / total * 100, 1) if total > 0 else 0.0
        result["computed_at"] = datetime.now(UTC).isoformat()

        await redis_manager.set("analytics:platform_stats", result, ttl=300)
        return result

    async def get_user_activity(self, user_id: uuid.UUID, days: int = 30) -> dict:
        """Return per-day submission heatmap and streak info for a user."""
        from sqlalchemy import text

        since = datetime.now(UTC) - timedelta(days=days)
        rows = (await self.db.execute(text("""
            SELECT DATE(created_at) as day, COUNT(*) as count,
                   SUM(CASE WHEN status = 'accepted' THEN 1 ELSE 0 END) as accepted
            FROM submissions
            WHERE user_id = :uid AND created_at >= :since
            GROUP BY DATE(created_at)
            ORDER BY day
        """), {"uid": user_id, "since": since})).fetchall()

        return {
            "user_id": str(user_id),
            "days": days,
            "activity": [
                {"date": str(r.day), "total": r.count, "accepted": r.accepted}
                for r in rows
            ],
        }

    async def get_problem_trends(self, limit: int = 10) -> list[dict]:
        """Most attempted problems in the last 7 days."""
        from sqlalchemy import text

        rows = (await self.db.execute(text("""
            SELECT p.id, p.title, p.difficulty, COUNT(s.id) as attempts,
                   SUM(CASE WHEN s.status = 'accepted' THEN 1 ELSE 0 END) as accepted
            FROM problems p
            JOIN submissions s ON p.id = s.problem_id
            WHERE s.created_at >= NOW() - INTERVAL '7 days'
            GROUP BY p.id, p.title, p.difficulty
            ORDER BY attempts DESC
            LIMIT :limit
        """), {"limit": limit})).fetchall()

        return [
            {
                "problem_id": str(r.id),
                "title": r.title,
                "difficulty": r.difficulty,
                "attempts": r.attempts,
                "accepted": r.accepted,
                "acceptance_rate": round(r.accepted / r.attempts * 100, 1) if r.attempts else 0,
            }
            for r in rows
        ]
