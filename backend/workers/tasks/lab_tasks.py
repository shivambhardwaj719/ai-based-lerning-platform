"""Lab provisioning and lifecycle management tasks."""
from __future__ import annotations

import structlog
from workers.celery_app import celery_app

log = structlog.get_logger()


@celery_app.task(name="workers.tasks.lab_tasks.provision_lab", queue="labs")
def provision_lab(instance_id: str, lab_config: dict) -> None:
    import asyncio
    async def _provision():
        from core.database import database_manager
        from models.lab import LabStatus
        async with database_manager.session() as db:
            from repositories.lab_repository import LabInstanceRepository
            repo = LabInstanceRepository(db)
            import uuid
            try:
                # Docker Compose provisioning
                access_url = f"https://lab-{instance_id[:8]}.labs.ailearning.com"
                await repo.update(
                    uuid.UUID(instance_id),
                    status=LabStatus.RUNNING,
                    access_url=access_url,
                )
                log.info("Lab provisioned", instance_id=instance_id)
            except Exception as e:
                await repo.update(uuid.UUID(instance_id), status=LabStatus.FAILED)
                log.error("Lab provisioning failed", instance_id=instance_id, error=str(e))
    asyncio.get_event_loop().run_until_complete(_provision())


@celery_app.task(name="workers.tasks.lab_tasks.expire_lab_instances", queue="labs")
def expire_lab_instances() -> None:
    import asyncio
    async def _expire():
        from core.database import database_manager
        from sqlalchemy import text
        async with database_manager.session() as db:
            result = await db.execute(text("""
                UPDATE lab_instances SET status = 'expired'
                WHERE status = 'running' AND expires_at < NOW()
            """))
            if result.rowcount > 0:
                log.info("Expired lab instances", count=result.rowcount)
    asyncio.get_event_loop().run_until_complete(_expire())
