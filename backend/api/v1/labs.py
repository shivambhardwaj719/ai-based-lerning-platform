"""DevOps Labs and AI/ML Playground API."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import CurrentUser, VerifiedUser
from core.database import get_db
from core.exceptions import NotFoundError, ServiceUnavailableError
from core.kafka import Topics, kafka_manager

router = APIRouter(prefix="/labs", tags=["Labs"])


@router.get("")
async def list_labs(
    db: AsyncSession = Depends(get_db),
    lab_type: str | None = Query(None),
    difficulty: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
) -> dict:
    from repositories.lab_repository import LabRepository
    repo = LabRepository(db)
    labs, total = await repo.get_published_labs(
        lab_type=lab_type, difficulty=difficulty,
        limit=page_size, offset=(page - 1) * page_size
    )
    return {"labs": labs, "total": total, "page": page}


@router.get("/{slug}")
async def get_lab(slug: str, db: AsyncSession = Depends(get_db)) -> dict:
    from repositories.lab_repository import LabRepository
    repo = LabRepository(db)
    lab = await repo.get_by_slug(slug)
    if not lab:
        raise NotFoundError("Lab")
    return {"lab": lab}


@router.post("/{lab_id}/start")
async def start_lab(
    lab_id: uuid.UUID,
    current_user: VerifiedUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Provision a lab environment for the user."""
    from repositories.lab_repository import LabRepository, LabInstanceRepository
    from models.lab import LabStatus
    from datetime import UTC, datetime, timedelta

    lab_repo = LabRepository(db)
    lab = await lab_repo.get_by_id(lab_id)
    if not lab:
        raise NotFoundError("Lab")

    instance_repo = LabInstanceRepository(db)
    instance = await instance_repo.create(
        lab_id=lab_id,
        user_id=current_user.id,
        status=LabStatus.PROVISIONING,
        expires_at=datetime.now(UTC) + timedelta(minutes=lab.max_duration_minutes),
    )

    # Async provisioning via Kafka
    await kafka_manager.publish(
        Topics.LAB_STARTED,
        "lab.start_provisioning",
        {
            "instance_id": str(instance.id),
            "lab_id": str(lab_id),
            "user_id": str(current_user.id),
            "docker_compose": lab.docker_compose_config,
        },
    )

    return {
        "instance_id": str(instance.id),
        "status": "provisioning",
        "message": "Lab is being provisioned. Check status endpoint.",
    }


@router.get("/{lab_id}/instances/{instance_id}")
async def get_lab_instance(
    lab_id: uuid.UUID,
    instance_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    from repositories.lab_repository import LabInstanceRepository
    repo = LabInstanceRepository(db)
    instance = await repo.get_by_id(instance_id)
    if not instance or instance.user_id != current_user.id:
        raise NotFoundError("Lab instance")
    return {"instance": instance}


@router.post("/{lab_id}/instances/{instance_id}/stop")
async def stop_lab(
    lab_id: uuid.UUID,
    instance_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    from repositories.lab_repository import LabInstanceRepository
    from models.lab import LabStatus

    repo = LabInstanceRepository(db)
    instance = await repo.get_by_id(instance_id)
    if not instance or instance.user_id != current_user.id:
        raise NotFoundError("Lab instance")

    await repo.update(instance_id, status=LabStatus.COMPLETED)
    await kafka_manager.publish(
        Topics.LAB_COMPLETED,
        "lab.stop",
        {"instance_id": str(instance_id), "user_id": str(current_user.id)},
    )
    return {"message": "Lab stopped"}
