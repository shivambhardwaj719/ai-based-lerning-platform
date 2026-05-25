"""Problem and Submission repository."""
from __future__ import annotations

import uuid

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.problem import Problem, Submission, SubmissionStatus, TestCase
from repositories.base import BaseRepository


class ProblemRepository(BaseRepository[Problem]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Problem, db)

    async def get_by_slug(self, slug: str) -> Problem | None:
        stmt = (
            select(Problem)
            .where(Problem.slug == slug)
            .options(selectinload(Problem.test_cases))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_published_problems(
        self,
        difficulty: str | None = None,
        tags: list[str] | None = None,
        problem_type: str | None = None,
        is_premium: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Problem], int]:
        filters = [Problem.is_published == True]
        if difficulty:
            filters.append(Problem.difficulty == difficulty)
        if problem_type:
            filters.append(Problem.problem_type == problem_type)
        if is_premium is not None:
            filters.append(Problem.is_premium == is_premium)
        if tags:
            filters.append(Problem.tags.overlap(tags))

        stmt = select(Problem).where(and_(*filters)).limit(limit).offset(offset)
        count_stmt = select(func.count()).select_from(Problem).where(and_(*filters))

        result = await self.session.execute(stmt)
        count_result = await self.session.execute(count_stmt)

        return list(result.scalars().all()), count_result.scalar_one()

    async def increment_submission_count(self, problem_id: uuid.UUID, accepted: bool) -> None:
        updates: dict = {"total_submissions": Problem.total_submissions + 1}
        if accepted:
            updates["accepted_submissions"] = Problem.accepted_submissions + 1
        await self.session.execute(
            update(Problem)
            .where(Problem.id == problem_id)
            .values(**updates)
        )

    async def get_sample_test_cases(self, problem_id: uuid.UUID) -> list[TestCase]:
        stmt = select(TestCase).where(
            and_(TestCase.problem_id == problem_id, TestCase.is_sample == True)
        ).order_by(TestCase.order_index)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_test_cases(self, problem_id: uuid.UUID) -> list[TestCase]:
        stmt = select(TestCase).where(
            TestCase.problem_id == problem_id
        ).order_by(TestCase.order_index)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class SubmissionRepository(BaseRepository[Submission]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Submission, db)

    async def get_user_submissions(
        self,
        user_id: uuid.UUID,
        problem_id: uuid.UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Submission]:
        filters = [Submission.user_id == user_id]
        if problem_id:
            filters.append(Submission.problem_id == problem_id)
        return await self.get_all(
            filters=filters,
            order_by=[Submission.created_at.desc()],
            limit=limit,
            offset=offset,
        )

    async def has_solved_problem(self, user_id: uuid.UUID, problem_id: uuid.UUID) -> bool:
        stmt = select(func.count()).select_from(Submission).where(
            and_(
                Submission.user_id == user_id,
                Submission.problem_id == problem_id,
                Submission.status == SubmissionStatus.ACCEPTED,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() > 0

    async def get_contest_submissions(self, contest_id: uuid.UUID) -> list[Submission]:
        stmt = select(Submission).where(Submission.contest_id == contest_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
