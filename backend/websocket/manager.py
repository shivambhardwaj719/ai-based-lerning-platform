"""
WebSocket Connection Manager: handles rooms, presence, and message broadcasting.
Supports contest rooms, AI streaming, collaborative coding, and notifications.
"""
from __future__ import annotations

import asyncio
import json
import uuid
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

import structlog
from fastapi import WebSocket, WebSocketDisconnect

from core.redis import redis_manager

log = structlog.get_logger()


class ConnectionInfo:
    def __init__(self, websocket: WebSocket, user_id: str, room_id: str, metadata: dict | None = None):
        self.websocket = websocket
        self.user_id = user_id
        self.room_id = room_id
        self.connected_at = datetime.now(UTC)
        self.metadata = metadata or {}
        self.conn_id = str(uuid.uuid4())


class WebSocketManager:
    """Central WebSocket manager with room-based broadcasting and Redis pub/sub."""

    def __init__(self) -> None:
        # room_id -> list of connections
        self._rooms: dict[str, list[ConnectionInfo]] = defaultdict(list)
        # user_id -> list of connections (multi-tab support)
        self._users: dict[str, list[ConnectionInfo]] = defaultdict(list)
        # conn_id -> ConnectionInfo
        self._connections: dict[str, ConnectionInfo] = {}

    async def connect(
        self,
        websocket: WebSocket,
        user_id: str,
        room_id: str,
        metadata: dict | None = None,
    ) -> ConnectionInfo:
        await websocket.accept()
        conn = ConnectionInfo(websocket, user_id, room_id, metadata)

        self._rooms[room_id].append(conn)
        self._users[user_id].append(conn)
        self._connections[conn.conn_id] = conn

        # Update presence in Redis
        await redis_manager.sadd(f"presence:{room_id}", user_id)
        await redis_manager.set(f"user:online:{user_id}", "1", ttl=300)

        # Broadcast join event
        await self.broadcast_to_room(room_id, {
            "type": "user_joined",
            "user_id": user_id,
            "timestamp": conn.connected_at.isoformat(),
            "online_count": len(await self.get_room_users(room_id)),
        }, exclude_conn=conn.conn_id)

        log.info("WebSocket connected", user_id=user_id, room_id=room_id, conn_id=conn.conn_id)
        return conn

    async def disconnect(self, conn: ConnectionInfo) -> None:
        room_id = conn.room_id
        user_id = conn.user_id

        self._rooms[room_id] = [c for c in self._rooms[room_id] if c.conn_id != conn.conn_id]
        self._users[user_id] = [c for c in self._users[user_id] if c.conn_id != conn.conn_id]
        self._connections.pop(conn.conn_id, None)

        # Clean up empty rooms
        if not self._rooms[room_id]:
            del self._rooms[room_id]

        # Update presence
        if not self._users[user_id]:
            await redis_manager.srem(f"presence:{room_id}", user_id)
            await redis_manager.delete(f"user:online:{user_id}")

        # Broadcast leave event
        await self.broadcast_to_room(room_id, {
            "type": "user_left",
            "user_id": user_id,
            "timestamp": datetime.now(UTC).isoformat(),
        })

        log.info("WebSocket disconnected", user_id=user_id, room_id=room_id)

    async def send_to_connection(self, conn: ConnectionInfo, message: dict) -> None:
        try:
            await conn.websocket.send_json(message)
        except Exception:
            await self.disconnect(conn)

    async def send_to_user(self, user_id: str, message: dict) -> None:
        conns = self._users.get(user_id, [])
        await asyncio.gather(*(self.send_to_connection(c, message) for c in conns), return_exceptions=True)

    async def broadcast_to_room(
        self,
        room_id: str,
        message: dict,
        exclude_conn: str | None = None,
    ) -> None:
        conns = [c for c in self._rooms.get(room_id, []) if c.conn_id != exclude_conn]
        await asyncio.gather(*(self.send_to_connection(c, message) for c in conns), return_exceptions=True)

    async def broadcast_to_all(self, message: dict) -> None:
        all_conns = list(self._connections.values())
        await asyncio.gather(*(self.send_to_connection(c, message) for c in all_conns), return_exceptions=True)

    async def get_room_users(self, room_id: str) -> set[str]:
        return await redis_manager.smembers(f"presence:{room_id}")

    def get_room_connection_count(self, room_id: str) -> int:
        return len(self._rooms.get(room_id, []))

    def get_total_connections(self) -> int:
        return len(self._connections)

    async def stream_text(self, conn: ConnectionInfo, text_generator) -> None:
        """Stream text chunks to a connection (AI responses)."""
        async for chunk in text_generator:
            await self.send_to_connection(conn, {"type": "stream_chunk", "content": chunk})
        await self.send_to_connection(conn, {"type": "stream_done"})


ws_manager = WebSocketManager()
