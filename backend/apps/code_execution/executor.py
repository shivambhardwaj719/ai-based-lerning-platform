"""
Secure Code Execution Engine with Docker sandbox isolation.
Supports Python, Java, JS, TS, Go, Rust, C++, Kotlin.
Enforces CPU, memory, and time limits via Docker resource constraints.
"""
from __future__ import annotations

import asyncio
import json
import os
import tempfile
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import docker
import structlog

from core.config import settings

log = structlog.get_logger()


@dataclass
class ExecutionResult:
    status: str
    stdout: str = ""
    stderr: str = ""
    runtime_ms: int = 0
    memory_used_mb: float = 0.0
    test_results: list[dict] = field(default_factory=list)
    compile_error: str | None = None


LANGUAGE_CONFIG = {
    "python": {
        "image": "python:3.11-alpine",
        "file": "solution.py",
        "compile_cmd": None,
        "run_cmd": "python solution.py",
        "timeout": 5,
    },
    "java": {
        "image": "openjdk:17-alpine",
        "file": "Solution.java",
        "compile_cmd": "javac Solution.java",
        "run_cmd": "java -Xmx256m Solution",
        "timeout": 10,
    },
    "javascript": {
        "image": "node:18-alpine",
        "file": "solution.js",
        "compile_cmd": None,
        "run_cmd": "node solution.js",
        "timeout": 5,
    },
    "typescript": {
        "image": "node:18-alpine",
        "file": "solution.ts",
        "compile_cmd": "npx tsc solution.ts --outDir /tmp/build",
        "run_cmd": "node /tmp/build/solution.js",
        "timeout": 10,
    },
    "go": {
        "image": "golang:1.21-alpine",
        "file": "solution.go",
        "compile_cmd": "go build -o solution_bin solution.go",
        "run_cmd": "./solution_bin",
        "timeout": 5,
    },
    "rust": {
        "image": "rust:1.74-alpine",
        "file": "solution.rs",
        "compile_cmd": "rustc -O solution.rs -o solution_bin",
        "run_cmd": "./solution_bin",
        "timeout": 15,
    },
    "cpp": {
        "image": "gcc:13-bookworm",
        "file": "solution.cpp",
        "compile_cmd": "g++ -O2 -std=c++17 solution.cpp -o solution_bin",
        "run_cmd": "./solution_bin",
        "timeout": 5,
    },
    "c": {
        "image": "gcc:13-bookworm",
        "file": "solution.c",
        "compile_cmd": "gcc -O2 solution.c -o solution_bin",
        "run_cmd": "./solution_bin",
        "timeout": 5,
    },
    "kotlin": {
        "image": "openjdk:17-alpine",
        "file": "Solution.kt",
        "compile_cmd": "kotlinc Solution.kt -include-runtime -d solution.jar",
        "run_cmd": "java -jar solution.jar",
        "timeout": 15,
    },
}


class CodeExecutor:
    """Executes code in isolated Docker containers with resource limits."""

    def __init__(self) -> None:
        self._docker = docker.from_env()

    async def run(
        self,
        code: str,
        language: str,
        test_cases: list[dict],
        custom_input: str | None = None,
        time_limit_ms: int = 2000,
        memory_limit_mb: int = 256,
    ) -> dict:
        config = LANGUAGE_CONFIG.get(language.lower())
        if not config:
            return {"status": "internal_error", "stderr": f"Unsupported language: {language}"}

        # Run in thread pool to avoid blocking async loop
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._execute_sync,
            code,
            language.lower(),
            config,
            test_cases,
            custom_input,
            time_limit_ms,
            memory_limit_mb,
        )
        return result

    def _execute_sync(
        self,
        code: str,
        language: str,
        config: dict,
        test_cases: list[dict],
        custom_input: str | None,
        time_limit_ms: int,
        memory_limit_mb: int,
    ) -> dict:
        with tempfile.TemporaryDirectory() as tmpdir:
            code_file = Path(tmpdir) / config["file"]
            code_file.write_text(code)

            # Step 1: Compile if needed
            if config.get("compile_cmd"):
                compile_result = self._run_in_container(
                    config["image"],
                    config["compile_cmd"],
                    tmpdir,
                    timeout=30,
                    memory_limit_mb=512,
                )
                if compile_result["exit_code"] != 0:
                    return {
                        "status": "compilation_error",
                        "compile_error": compile_result["stderr"][:2000],
                        "stdout": "",
                        "stderr": compile_result["stderr"][:2000],
                        "runtime_ms": 0,
                        "memory_used_mb": 0.0,
                        "test_results": [],
                    }

            # Step 2: Run against test cases
            if custom_input is not None:
                return self._run_single(config, tmpdir, custom_input, time_limit_ms, memory_limit_mb)

            test_results = []
            all_passed = True
            total_runtime = 0

            for tc in test_cases:
                result = self._run_single(
                    config, tmpdir, tc["input"], time_limit_ms, memory_limit_mb
                )
                passed = result.get("status") == "ok" and result.get("stdout", "").strip() == tc.get("expected", "").strip()
                total_runtime += result.get("runtime_ms", 0)

                test_results.append({
                    "passed": passed,
                    "input": tc["input"][:200],
                    "expected": tc.get("expected", "")[:200],
                    "actual": result.get("stdout", "")[:200],
                    "runtime_ms": result.get("runtime_ms", 0),
                    "status": result.get("status", "unknown"),
                    "stderr": result.get("stderr", "")[:500],
                })

                if not passed:
                    all_passed = False
                if result.get("status") not in ("ok",):
                    break

            passed_count = sum(1 for r in test_results if r["passed"])
            return {
                "status": "accepted" if all_passed else test_results[-1].get("status", "wrong_answer") if test_results else "wrong_answer",
                "stdout": test_results[0]["actual"] if test_results else "",
                "stderr": test_results[-1]["stderr"] if test_results else "",
                "runtime_ms": max((r["runtime_ms"] for r in test_results), default=0),
                "memory_used_mb": 0.0,
                "test_results": test_results,
            }

    def _run_single(self, config: dict, tmpdir: str, stdin: str, time_limit_ms: int, memory_mb: int) -> dict:
        start = time.perf_counter()
        result = self._run_in_container(
            config["image"],
            config["run_cmd"],
            tmpdir,
            stdin=stdin,
            timeout=max(time_limit_ms / 1000 + 1, 5),
            memory_limit_mb=memory_mb,
        )
        elapsed_ms = int((time.perf_counter() - start) * 1000)

        if result["timed_out"]:
            return {"status": "time_limit_exceeded", "runtime_ms": elapsed_ms, "stdout": "", "stderr": ""}
        if result["exit_code"] != 0 and result["stderr"]:
            return {"status": "runtime_error", "runtime_ms": elapsed_ms, "stdout": result["stdout"], "stderr": result["stderr"]}
        return {"status": "ok", "runtime_ms": elapsed_ms, "stdout": result["stdout"], "stderr": result["stderr"]}

    def _run_in_container(
        self,
        image: str,
        command: str,
        workdir: str,
        stdin: str = "",
        timeout: float = 10,
        memory_limit_mb: int = 256,
    ) -> dict:
        try:
            container = self._docker.containers.run(
                image=image,
                command=["sh", "-c", command],
                volumes={workdir: {"bind": "/sandbox", "mode": "rw"}},
                working_dir="/sandbox",
                stdin_open=True,
                stdout=True,
                stderr=True,
                remove=True,
                network_disabled=True,
                read_only=False,
                mem_limit=f"{memory_limit_mb}m",
                memswap_limit=f"{memory_limit_mb}m",
                cpu_period=100000,
                cpu_quota=settings.CODE_EXECUTION_CPU_QUOTA,
                pids_limit=100,
                cap_drop=["ALL"],
                security_opt=["no-new-privileges"],
                detach=False,
                timeout=int(timeout) + 2,
                environment={"HOME": "/sandbox"},
                input=stdin.encode() if stdin else None,
            )
            return {
                "stdout": container.decode("utf-8", errors="replace") if isinstance(container, bytes) else "",
                "stderr": "",
                "exit_code": 0,
                "timed_out": False,
            }
        except docker.errors.ContainerError as e:
            return {
                "stdout": e.stderr.decode("utf-8", errors="replace") if e.stderr else "",
                "stderr": e.stderr.decode("utf-8", errors="replace") if e.stderr else str(e),
                "exit_code": e.exit_status,
                "timed_out": False,
            }
        except Exception as e:
            timed_out = "timeout" in str(e).lower()
            return {
                "stdout": "",
                "stderr": str(e) if not timed_out else "",
                "exit_code": -1,
                "timed_out": timed_out,
            }


class PlagiarismDetector:
    """Detects code plagiarism using token-based similarity (Moss algorithm)."""

    def compute_similarity(self, code1: str, code2: str, language: str) -> float:
        tokens1 = self._tokenize(code1, language)
        tokens2 = self._tokenize(code2, language)

        if not tokens1 or not tokens2:
            return 0.0

        # Jaccard similarity on k-grams
        k = 5
        grams1 = set(self._kgrams(tokens1, k))
        grams2 = set(self._kgrams(tokens2, k))

        if not grams1 and not grams2:
            return 0.0

        intersection = grams1 & grams2
        union = grams1 | grams2
        return len(intersection) / len(union) if union else 0.0

    def _tokenize(self, code: str, language: str) -> list[str]:
        # Simple whitespace tokenization
        import re
        return re.findall(r'\w+|[^\w\s]', code)

    def _kgrams(self, tokens: list, k: int) -> list[tuple]:
        return [tuple(tokens[i:i+k]) for i in range(len(tokens) - k + 1)]
