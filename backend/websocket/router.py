"""
WebSocket route handlers for contests, AI streaming, collaboration, and notifications.
"""
from __future__ import annotations

import json
import uuid

import structlog
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from auth.jwt import get_token_from_header, verify_access_token
from core.database import get_db
from core.exceptions import AuthenticationError
from websocket.manager import ws_manager

log = structlog.get_logger()
websocket_router = APIRouter()


async def _authenticate_ws(websocket: WebSocket) -> dict:
    """Authenticate WebSocket via token query param."""
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Authentication required")
        raise AuthenticationError()
    try:
        payload = await verify_access_token(token)
        return payload
    except Exception:
        await websocket.close(code=4001, reason="Invalid token")
        raise AuthenticationError()


@websocket_router.websocket("/contest/{contest_id}")
async def contest_websocket(contest_id: uuid.UUID, websocket: WebSocket) -> None:
    """Real-time contest updates: leaderboard, submissions, announcements."""
    payload = await _authenticate_ws(websocket)
    user_id = payload["sub"]
    room_id = f"contest:{contest_id}"

    conn = await ws_manager.connect(websocket, user_id, room_id)

    # Send current leaderboard on connect
    from core.redis import redis_manager
    leaderboard = await redis_manager.get(f"contest:leaderboard:{contest_id}:1")
    if leaderboard:
        await ws_manager.send_to_connection(conn, {"type": "leaderboard_init", "data": leaderboard})

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "")

            if msg_type == "ping":
                await ws_manager.send_to_connection(conn, {"type": "pong"})
            elif msg_type == "chat":
                await ws_manager.broadcast_to_room(room_id, {
                    "type": "chat_message",
                    "user_id": user_id,
                    "message": data.get("message", "")[:500],
                })
    except WebSocketDisconnect:
        await ws_manager.disconnect(conn)


@websocket_router.websocket("/ai/stream")
async def ai_stream_websocket(websocket: WebSocket) -> None:
    """Bidirectional AI streaming with real-time responses."""
    payload = await _authenticate_ws(websocket)
    user_id = payload["sub"]
    room_id = f"ai:user:{user_id}"

    conn = await ws_manager.connect(websocket, user_id, room_id)

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "")

            if msg_type == "chat":
                await ws_manager.send_to_connection(conn, {"type": "thinking"})
                # Stream AI response
                from ai.agents.mentor_agent import MentorAgent
                from core.database import database_manager
                async with database_manager.session() as db:
                    agent = MentorAgent(user_id=uuid.UUID(user_id), db=db)
                    async for chunk in agent.stream_response(
                        message=data.get("message", ""),
                        conversation_id=data.get("conversation_id"),
                        conversation_type=data.get("conversation_type", "general"),
                    ):
                        await ws_manager.send_to_connection(conn, {"type": "stream", "chunk": chunk})

            elif msg_type == "ping":
                await ws_manager.send_to_connection(conn, {"type": "pong"})

    except WebSocketDisconnect:
        await ws_manager.disconnect(conn)


@websocket_router.websocket("/collaboration/{room_id}")
async def collaboration_websocket(room_id: str, websocket: WebSocket) -> None:
    """Collaborative coding: cursor positions, code changes (CRDT-style)."""
    payload = await _authenticate_ws(websocket)
    user_id = payload["sub"]
    full_room = f"collab:{room_id}"

    conn = await ws_manager.connect(websocket, user_id, full_room)

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "")

            if msg_type == "code_change":
                await ws_manager.broadcast_to_room(full_room, {
                    "type": "code_change",
                    "user_id": user_id,
                    "delta": data.get("delta"),
                    "cursor_position": data.get("cursor_position"),
                }, exclude_conn=conn.conn_id)

            elif msg_type == "cursor_move":
                await ws_manager.broadcast_to_room(full_room, {
                    "type": "cursor_move",
                    "user_id": user_id,
                    "position": data.get("position"),
                }, exclude_conn=conn.conn_id)

            elif msg_type == "ping":
                await ws_manager.send_to_connection(conn, {"type": "pong"})

    except WebSocketDisconnect:
        await ws_manager.disconnect(conn)


@websocket_router.websocket("/notifications")
async def notifications_websocket(websocket: WebSocket) -> None:
    """Real-time notification delivery."""
    payload = await _authenticate_ws(websocket)
    user_id = payload["sub"]
    room_id = f"notifications:{user_id}"

    conn = await ws_manager.connect(websocket, user_id, room_id)

    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "ping":
                await ws_manager.send_to_connection(conn, {"type": "pong"})
    except WebSocketDisconnect:
        await ws_manager.disconnect(conn)


@websocket_router.websocket("/submission/{submission_id}")
async def submission_status_websocket(submission_id: uuid.UUID, websocket: WebSocket) -> None:
    """Real-time submission status updates."""
    payload = await _authenticate_ws(websocket)
    user_id = payload["sub"]
    room_id = f"submission:{submission_id}"

    conn = await ws_manager.connect(websocket, user_id, room_id)

    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "ping":
                await ws_manager.send_to_connection(conn, {"type": "pong"})
    except WebSocketDisconnect:
        await ws_manager.disconnect(conn)
