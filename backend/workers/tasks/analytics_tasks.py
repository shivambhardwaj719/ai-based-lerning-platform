"""
Analytics tasks: user activity tracking, leaderboard updates,
platform statistics, trend analysis, and reporting.
"""
from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

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
    name="workers.tasks.analytics_tasks.update_global_leaderboard",
    queue="analytics",
)
def update_global_leaderboard() -> None:
    """Rebuild the global leaderboard Redis sorted set from DB."""
    log.info("Updating global leaderboard")

    async def _update():
        from core.database import database_manager
        from core.redis import redis_manager
        from sqlalchemy import text

        async with database_manager.session() as db:
            result = await db.execute(text("""
                SELECT u.id, u.username, up.total_points, up.rating, up.problems_solved
                FROM users u
                JOIN user_profiles up ON u.id = up.user_id
                WHERE u.status = 'active'
                ORDER BY up.total_points DESC
                LIMIT 10000
            """))
            rows = result.fetchall()

        if not rows:
            return

        pipe = redis_manager.pipeline()
        for row in rows:
            pipe.zadd("leaderboard:global", {str(row.id): float(row.total_points)})
        await pipe.execute()

        # Store top 100 with full details
        top_100 = [
            {
                "rank": idx + 1,
                "user_id": str(row.id),
                "username": row.username,
                "total_points": row.total_points,
                "rating": row.rating,
                "problems_solved": row.problems_solved,
            }
            for idx, row in enumerate(rows[:100])
        ]
        await redis_manager.set("leaderboard:global:top100", top_100, ttl=900)
        log.info("Global leaderboard updated", total_users=len(rows))

    run_async(_update())


@celery_app.task(
    name="workers.tasks.analytics_tasks.track_daily_active_users",
    queue="analytics",
)
def track_daily_active_users() -> None:
    """Count and store daily active users metric."""
    log.info("Tracking daily active users")

    async def _track():
        from core.database import database_manager
        from core.redis import redis_manager
        from sqlalchemy import text

        async with database_manager.session() as db:
            result = await db.execute(text("""
                SELECT COUNT(DISTINCT user_id)
                FROM audit_logs
                WHERE created_at >= NOW() - INTERVAL '24 hours'
                AND success = true
            """))
            dau = result.scalar_one() or 0

        today = datetime.now(UTC).strftime("%Y-%m-%d")
        await redis_manager.set(f"analytics:dau:{today}", dau, ttl=86400 * 7)
        await redis_manager.incr("analytics:dau:total")
        log.info("DAU tracked", dau=dau, date=today)

    run_async(_track())


@celery_app.task(
    name="workers.tasks.analytics_tasks.compute_problem_stats",
    queue="analytics",
)
def compute_problem_stats() -> None:
    """Recompute acceptance rates and difficulty scores for all problems."""
    log.info("Computing problem statistics")

    async def _compute():
        from core.database import database_manager
        from sqlalchemy import text

        async with database_manager.session() as db:
            await db.execute(text("""
                UPDATE problems p
                SET
                    acceptance_rate = CASE
                        WHEN total_submissions > 0
                        THEN ROUND((accepted_submissions::numeric / total_submissions) * 100, 2)
                        ELSE 0
                    END
                WHERE is_published = true
            """))
            log.info("Problem stats recomputed")

    run_async(_compute())


@celery_app.task(
    name="workers.tasks.analytics_tasks.generate_daily_report",
    queue="analytics",
)
def generate_daily_report() -> dict:
    """Generate a comprehensive daily platform report."""
    log.info("Generating daily report")

    async def _generate():
        from core.database import database_manager
        from sqlalchemy import text

        async with database_manager.session() as db:
            new_users = (await db.execute(text(
                "SELECT COUNT(*) FROM users WHERE created_at >= NOW() - INTERVAL '24 hours'"
            ))).scalar_one()

            new_submissions = (await db.execute(text(
                "SELECT COUNT(*) FROM submissions WHERE created_at >= NOW() - INTERVAL '24 hours'"
            ))).scalar_one()

            accepted = (await db.execute(text(
                "SELECT COUNT(*) FROM submissions WHERE status = 'accepted' AND created_at >= NOW() - INTERVAL '24 hours'"
            ))).scalar_one()

            report = {
                "date": datetime.now(UTC).strftime("%Y-%m-%d"),
                "new_users": new_users,
                "new_submissions": new_submissions,
                "accepted_submissions": accepted,
                "acceptance_rate": round(accepted / new_submissions * 100, 1) if new_submissions > 0 else 0,
            }

        from core.redis import redis_manager
        await redis_manager.set(f"report:daily:{report['date']}", report, ttl=86400 * 30)
        log.info("Daily report generated", **report)
        return report

    return run_async(_generate())


@celery_app.task(
    name="workers.tasks.analytics_tasks.update_user_streaks",
    queue="analytics",
)
def update_user_streaks() -> None:
    """Update submission streaks for all active users."""
    log.info("Updating user streaks")

    async def _update():
        from core.database import database_manager
        from sqlalchemy import text

        async with database_manager.session() as db:
            # Users who submitted today get streak increment
            await db.execute(text("""
                UPDATE user_profiles up
                SET
                    streak_days = streak_days + 1,
                    max_streak_days = GREATEST(max_streak_days, streak_days + 1)
                WHERE up.user_id IN (
                    SELECT DISTINCT user_id FROM submissions
                    WHERE created_at >= NOW() - INTERVAL '1 day'
                    AND status = 'accepted'
                )
            """))
            # Reset streaks for users who didn't submit yesterday
            await db.execute(text("""
                UPDATE user_profiles up
                SET streak_days = 0
                WHERE streak_days > 0
                AND up.user_id NOT IN (
                    SELECT DISTINCT user_id FROM submissions
                    WHERE created_at >= NOW() - INTERVAL '2 days'
                )
            """))
        log.info("User streaks updated")

    run_async(_update())
