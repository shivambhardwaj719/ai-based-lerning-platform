"""Maintenance tasks: cleanup, leaderboard updates, contest status checks."""
from __future__ import annotations

import structlog
from workers.celery_app import celery_app

log = structlog.get_logger()


@celery_app.task(name="workers.tasks.maintenance_tasks.update_acceptance_rates", queue="maintenance")
def update_acceptance_rates() -> None:
    import asyncio
    async def _update():
        from core.database import database_manager
        from sqlalchemy import text
        async with database_manager.session() as db:
            await db.execute(text("""
                UPDATE problems SET acceptance_rate =
                    CASE WHEN total_submissions > 0
                    THEN (accepted_submissions::float / total_submissions * 100)
                    ELSE 0 END
            """))
    asyncio.get_event_loop().run_until_complete(_update())


@celery_app.task(name="workers.tasks.maintenance_tasks.cleanup_expired_sessions", queue="maintenance")
def cleanup_expired_sessions() -> None:
    import asyncio
    async def _cleanup():
        from core.database import database_manager
        from sqlalchemy import text
        async with database_manager.session() as db:
            result = await db.execute(text(
                "DELETE FROM sessions WHERE expires_at < NOW() OR is_active = false AND updated_at < NOW() - INTERVAL '30 days'"
            ))
            log.info("Cleaned up sessions", deleted=result.rowcount)
    asyncio.get_event_loop().run_until_complete(_cleanup())


@celery_app.task(name="workers.tasks.maintenance_tasks.check_contest_status", queue="maintenance")
def check_contest_status() -> None:
    import asyncio
    async def _check():
        from core.database import database_manager
        from core.kafka import kafka_manager, Topics
        from sqlalchemy import text
        from datetime import UTC, datetime
        async with database_manager.session() as db:
            # Activate contests that should start
            await db.execute(text(
                "UPDATE contests SET status = 'active' WHERE status = 'upcoming' AND start_time <= NOW()"
            ))
            # End contests that should finish
            await db.execute(text(
                "UPDATE contests SET status = 'ended' WHERE status = 'active' AND end_time <= NOW()"
            ))
    asyncio.get_event_loop().run_until_complete(_check())


@celery_app.task(name="workers.tasks.analytics_tasks.update_global_leaderboard", queue="analytics")
def update_global_leaderboard() -> None:
    import asyncio
    async def _update():
        from core.database import database_manager
        from core.redis import redis_manager
        from sqlalchemy import text
        async with database_manager.session() as db:
            result = await db.execute(text("""
                SELECT u.id, u.username, up.total_points, up.rating
                FROM users u
                JOIN user_profiles up ON u.id = up.user_id
                ORDER BY up.total_points DESC
                LIMIT 1000
            """))
            rows = result.fetchall()
            pipe = redis_manager.pipeline()
            for row in rows:
                pipe.zadd("leaderboard:global", {str(row.id): float(row.total_points)})
            await pipe.execute()
    asyncio.get_event_loop().run_until_complete(_update())
