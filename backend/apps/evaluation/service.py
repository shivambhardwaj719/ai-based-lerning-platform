"""Submission evaluation service — orchestrates code execution and result storage."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog

log = structlog.get_logger()


class EvaluationService:
    """Run a submission against test cases and persist the result."""

    def __init__(self, db):
        self.db = db

    async def evaluate(self, submission_id: uuid.UUID) -> dict:
        """Full evaluation pipeline: fetch → execute → store → notify."""
        from apps.code_execution.executor import CodeExecutor
        from models.problem import SubmissionStatus
        from repositories.problem_repository import ProblemRepository, SubmissionRepository

        sub_repo = SubmissionRepository(self.db)
        prob_repo = ProblemRepository(self.db)

        submission = await sub_repo.get_by_id(submission_id)
        if not submission:
            raise ValueError(f"Submission {submission_id} not found")

        problem = await prob_repo.get_by_id(submission.problem_id)
        if not problem:
            raise ValueError(f"Problem {submission.problem_id} not found")

        await sub_repo.update(submission_id, status=SubmissionStatus.RUNNING)

        executor = CodeExecutor()
        test_cases = problem.test_cases or []
        passed = 0
        failed_case = None
        final_status = SubmissionStatus.ACCEPTED
        total_time = 0.0
        max_memory = 0

        for tc in test_cases:
            result = await executor.execute(
                code=submission.code,
                language=submission.language,
                stdin=tc.input_data or "",
                time_limit_seconds=problem.time_limit_ms / 1000,
                memory_limit_mb=problem.memory_limit_mb,
            )

            total_time += result.get("execution_time_ms", 0)
            max_memory = max(max_memory, result.get("memory_used_mb", 0))

            if result.get("timed_out"):
                final_status = SubmissionStatus.TIME_LIMIT_EXCEEDED
                failed_case = tc
                break
            if result.get("memory_exceeded"):
                final_status = SubmissionStatus.MEMORY_LIMIT_EXCEEDED
                failed_case = tc
                break
            if result.get("error"):
                final_status = SubmissionStatus.RUNTIME_ERROR
                failed_case = tc
                break

            actual = (result.get("stdout") or "").strip()
            expected = (tc.expected_output or "").strip()
            if actual != expected:
                final_status = SubmissionStatus.WRONG_ANSWER
                failed_case = tc
                break

            passed += 1

        avg_time = total_time / max(len(test_cases), 1)

        await sub_repo.update(
            submission_id,
            status=final_status,
            execution_time_ms=int(avg_time),
            memory_used_mb=max_memory,
            test_cases_passed=passed,
            test_cases_total=len(test_cases),
        )

        if final_status == SubmissionStatus.ACCEPTED:
            await self._update_user_stats(submission.user_id, submission.problem_id)

        log.info(
            "Evaluation complete",
            submission_id=str(submission_id),
            status=final_status.value,
            passed=passed,
            total=len(test_cases),
        )
        return {
            "submission_id": str(submission_id),
            "status": final_status.value,
            "passed": passed,
            "total": len(test_cases),
            "execution_time_ms": int(avg_time),
            "memory_used_mb": max_memory,
        }

    async def _update_user_stats(self, user_id: uuid.UUID, problem_id: uuid.UUID) -> None:
        """Increment solved problems count if not already solved."""
        from sqlalchemy import text
        await self.db.execute(text("""
            UPDATE user_profiles
            SET problems_solved = problems_solved + 1,
                total_points = total_points + (
                    SELECT COALESCE(points, 10) FROM problems WHERE id = :pid
                )
            WHERE user_id = :uid
            AND NOT EXISTS (
                SELECT 1 FROM submissions
                WHERE user_id = :uid AND problem_id = :pid
                AND status = 'accepted' AND id != (
                    SELECT id FROM submissions
                    WHERE user_id = :uid AND problem_id = :pid
                    ORDER BY created_at DESC LIMIT 1
                )
            )
        """), {"uid": user_id, "pid": problem_id})
