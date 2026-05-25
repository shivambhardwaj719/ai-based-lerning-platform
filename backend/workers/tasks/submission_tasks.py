"""
Submission evaluation tasks: execute code, evaluate results, update scores.
"""
from __future__ import annotations

import asyncio
import uuid

import structlog
from celery import Task

from workers.celery_app import celery_app

log = structlog.get_logger()


def run_async(coro):
    """Run async function in Celery (sync) context."""
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
    bind=True,
    name="workers.tasks.submission_tasks.evaluate_submission",
    queue="submissions",
    max_retries=3,
    default_retry_delay=10,
)
def evaluate_submission(self: Task, submission_id: str) -> dict:
    """Evaluate a code submission against all test cases."""
    log.info("Evaluating submission", submission_id=submission_id)

    async def _evaluate():
        from core.database import database_manager
        from core.redis import redis_manager
        from repositories.problem_repository import ProblemRepository, SubmissionRepository
        from apps.code_execution.executor import CodeExecutor, PlagiarismDetector
        from models.problem import SubmissionStatus
        from websocket.manager import ws_manager

        async with database_manager.session() as db:
            sub_repo = SubmissionRepository(db)
            submission = await sub_repo.get_by_id(uuid.UUID(submission_id))
            if not submission:
                return {"error": "Submission not found"}

            # Update status to running
            await sub_repo.update(submission.id, status=SubmissionStatus.RUNNING)

            # Notify user via WebSocket
            await redis_manager.publish(
                f"submission:{submission_id}",
                {"type": "status_update", "status": "running"},
            )

            # Fetch test cases
            problem_repo = ProblemRepository(db)
            test_cases = await problem_repo.get_all_test_cases(submission.problem_id)
            problem = await problem_repo.get_by_id(submission.problem_id)

            # Execute code
            executor = CodeExecutor()
            result = await executor.run(
                code=submission.code,
                language=submission.language,
                test_cases=[
                    {"input": tc.input_data, "expected": tc.expected_output}
                    for tc in test_cases
                ],
                time_limit_ms=problem.time_limit_ms,
                memory_limit_mb=problem.memory_limit_mb,
            )

            # Map result to submission status
            status_map = {
                "accepted": SubmissionStatus.ACCEPTED,
                "wrong_answer": SubmissionStatus.WRONG_ANSWER,
                "time_limit_exceeded": SubmissionStatus.TIME_LIMIT_EXCEEDED,
                "memory_limit_exceeded": SubmissionStatus.MEMORY_LIMIT_EXCEEDED,
                "runtime_error": SubmissionStatus.RUNTIME_ERROR,
                "compilation_error": SubmissionStatus.COMPILATION_ERROR,
            }
            status = status_map.get(result.get("status", ""), SubmissionStatus.INTERNAL_ERROR)

            passed = sum(1 for r in result.get("test_results", []) if r.get("passed", False))
            total = len(test_cases)
            score = (passed / total * 100) if total > 0 else 0.0

            # Check plagiarism (async background)
            plagiarism_score = 0.0

            # Update submission
            await sub_repo.update(
                submission.id,
                status=status,
                runtime_ms=result.get("runtime_ms"),
                memory_used_mb=result.get("memory_used_mb"),
                score=score,
                test_cases_passed=passed,
                test_cases_total=total,
                stdout=result.get("stdout", "")[:10000],
                stderr=result.get("stderr", "")[:5000],
                compile_error=result.get("compile_error", "")[:5000],
                test_results=result.get("test_results"),
                plagiarism_score=plagiarism_score,
            )

            # Update problem stats
            await problem_repo.increment_submission_count(
                submission.problem_id, accepted=status == SubmissionStatus.ACCEPTED
            )

            # Notify user via WebSocket
            await redis_manager.publish(
                f"submission:{submission_id}",
                {
                    "type": "result",
                    "status": status.value,
                    "score": score,
                    "test_cases_passed": passed,
                    "test_cases_total": total,
                    "runtime_ms": result.get("runtime_ms"),
                },
            )

            # Update user profile if accepted
            if status == SubmissionStatus.ACCEPTED:
                await _update_user_stats(db, submission.user_id, submission.problem_id)

            # Publish Kafka event
            from core.kafka import kafka_manager, Topics
            await kafka_manager.publish(
                Topics.SUBMISSION_COMPLETED,
                "submission.completed",
                {
                    "submission_id": submission_id,
                    "user_id": str(submission.user_id),
                    "problem_id": str(submission.problem_id),
                    "status": status.value,
                    "score": score,
                },
            )

            return {"status": status.value, "score": score}

    try:
        return run_async(_evaluate())
    except Exception as exc:
        log.error("Submission evaluation failed", submission_id=submission_id, error=str(exc))
        self.retry(exc=exc)


async def _update_user_stats(db, user_id, problem_id):
    from repositories.user_repository import UserRepository
    from repositories.problem_repository import SubmissionRepository
    sub_repo = SubmissionRepository(db)

    # Check if first time solving this problem
    from sqlalchemy import and_, func, select
    from models.problem import Submission, SubmissionStatus
    count_stmt = select(func.count()).select_from(Submission).where(
        and_(
            Submission.user_id == user_id,
            Submission.problem_id == problem_id,
            Submission.status == SubmissionStatus.ACCEPTED,
        )
    )
    result = await db.execute(count_stmt)
    accepted_count = result.scalar_one()

    if accepted_count == 1:  # First accepted submission
        from models.user import UserProfile
        from sqlalchemy import text
        await db.execute(
            text("UPDATE user_profiles SET problems_solved = problems_solved + 1, total_points = total_points + 10 WHERE user_id = :uid"),
            {"uid": user_id},
        )
