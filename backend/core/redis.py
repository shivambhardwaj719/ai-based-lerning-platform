"""
Redis client manager supporting pub/sub, caching, sessions, and distributed locks.
"""
from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from typing import Any

import structlog
from redis.asyncio import Redis, ConnectionPool
from redis.asyncio.lock import Lock

from core.config import settings

log = structlog.get_logger()


class RedisManager:
    """Central Redis manager with connection pooling and helper methods."""

    def __init__(self) -> None:
        self._pool: ConnectionPool | None = None
        self._client: Redis | None = None

    async def connect(self) -> None:
        self._pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=True,
        )
        self._client = Redis(connection_pool=self._pool)
        await self._client.ping()
        log.info("Redis connected")

    async def disconnect(self) -> None:
        if self._client:
            await self._client.aclose()
        if self._pool:
            await self._pool.aclose()
        log.info("Redis disconnected")

    async def health_check(self) -> bool:
        try:
            await self._client.ping()
            return True
        except Exception:
            return False

    @property
    def client(self) -> Redis:
        if not self._client:
            msg = "Redis not connected"
            raise RuntimeError(msg)
        return self._client

    # ── Cache helpers ─────────────────────────────────────────────────────────

    async def get(self, key: str) -> Any | None:
        value = await self.client.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        serialized = json.dumps(value) if not isinstance(value, str) else value
        if ttl:
            await self.client.setex(key, ttl, serialized)
        else:
            await self.client.set(key, serialized)

    async def delete(self, *keys: str) -> int:
        return await self.client.delete(*keys)

    async def exists(self, key: str) -> bool:
        return bool(await self.client.exists(key))

    async def expire(self, key: str, ttl: int) -> bool:
        return await self.client.expire(key, ttl)

    async def ttl(self, key: str) -> int:
        return await self.client.ttl(key)

    async def incr(self, key: str, amount: int = 1) -> int:
        return await self.client.incrby(key, amount)

    async def hset(self, name: str, mapping: dict) -> int:
        return await self.client.hset(name, mapping=mapping)

    async def hget(self, name: str, key: str) -> Any | None:
        return await self.client.hget(name, key)

    async def hgetall(self, name: str) -> dict:
        return await self.client.hgetall(name)

    async def hdel(self, name: str, *keys: str) -> int:
        return await self.client.hdel(name, *keys)

    async def sadd(self, name: str, *values: str) -> int:
        return await self.client.sadd(name, *values)

    async def srem(self, name: str, *values: str) -> int:
        return await self.client.srem(name, *values)

    async def smembers(self, name: str) -> set:
        return await self.client.smembers(name)

    async def sismember(self, name: str, value: str) -> bool:
        return bool(await self.client.sismember(name, value))

    async def lpush(self, name: str, *values: str) -> int:
        return await self.client.lpush(name, *values)

    async def lrange(self, name: str, start: int, end: int) -> list:
        return await self.client.lrange(name, start, end)

    async def zadd(self, name: str, mapping: dict) -> int:
        return await self.client.zadd(name, mapping)

    async def zrange(self, name: str, start: int, end: int, withscores: bool = False) -> list:
        return await self.client.zrange(name, start, end, withscores=withscores)

    async def zrevrange(self, name: str, start: int, end: int, withscores: bool = False) -> list:
        return await self.client.zrevrange(name, start, end, withscores=withscores)

    async def zscore(self, name: str, member: str) -> float | None:
        return await self.client.zscore(name, member)

    # ── Pub/Sub ───────────────────────────────────────────────────────────────

    async def publish(self, channel: str, message: Any) -> int:
        payload = json.dumps(message) if not isinstance(message, str) else message
        return await self.client.publish(channel, payload)

    def pubsub(self):
        return self.client.pubsub()

    # ── Distributed lock ──────────────────────────────────────────────────────

    def lock(self, name: str, timeout: int = 10) -> Lock:
        return self.client.lock(f"lock:{name}", timeout=timeout)

    # ── Pipeline ──────────────────────────────────────────────────────────────

    def pipeline(self):
        return self.client.pipeline()

    # ── Session helpers ───────────────────────────────────────────────────────

    async def set_session(self, session_id: str, data: dict, ttl: int | None = None) -> None:
        await self.set(
            f"session:{session_id}",
            data,
            ttl or settings.REDIS_SESSION_TTL,
        )

    async def get_session(self, session_id: str) -> dict | None:
        return await self.get(f"session:{session_id}")

    async def delete_session(self, session_id: str) -> None:
        await self.delete(f"session:{session_id}")

    # ── Rate limit helpers ────────────────────────────────────────────────────

    async def rate_limit_check(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        """Returns (is_allowed, remaining_count)."""
        pipe = self.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        results = await pipe.execute()
        count = results[0]
        remaining = max(0, limit - count)
        return count <= limit, remaining


redis_manager = RedisManager()


async def get_redis() -> AsyncGenerator[Redis, None]:
    """FastAPI dependency: yields the Redis client."""
    yield redis_manager.client
