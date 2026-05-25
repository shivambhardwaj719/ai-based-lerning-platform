"""
Kafka event streaming manager for async producer/consumer operations.
Supports topic management, schema registry, and dead-letter queues.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Callable

import structlog
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaError

from core.config import settings

log = structlog.get_logger()


# ── Topic Definitions ─────────────────────────────────────────────────────────
class Topics:
    # Auth events
    USER_REGISTERED = "user.registered"
    USER_LOGGED_IN = "user.logged_in"
    USER_PASSWORD_RESET = "user.password_reset"
    USER_EMAIL_VERIFIED = "user.email_verified"

    # Submission events
    SUBMISSION_CREATED = "submission.created"
    SUBMISSION_EVALUATED = "submission.evaluated"
    SUBMISSION_COMPLETED = "submission.completed"

    # Contest events
    CONTEST_STARTED = "contest.started"
    CONTEST_ENDED = "contest.ended"
    CONTEST_SUBMISSION = "contest.submission"
    CONTEST_LEADERBOARD_UPDATED = "contest.leaderboard_updated"

    # AI events
    AI_CONVERSATION_STARTED = "ai.conversation_started"
    AI_RESPONSE_GENERATED = "ai.response_generated"
    AI_ROADMAP_GENERATED = "ai.roadmap_generated"

    # Notification events
    NOTIFICATION_SEND = "notification.send"
    EMAIL_SEND = "email.send"
    PUSH_NOTIFICATION_SEND = "push_notification.send"

    # Analytics events
    ANALYTICS_EVENT = "analytics.event"
    USER_ACTIVITY = "user.activity"
    PAGE_VIEW = "page.view"

    # Payment events
    PAYMENT_CREATED = "payment.created"
    PAYMENT_COMPLETED = "payment.completed"
    PAYMENT_FAILED = "payment.failed"
    SUBSCRIPTION_ACTIVATED = "subscription.activated"
    SUBSCRIPTION_CANCELLED = "subscription.cancelled"

    # Lab events
    LAB_STARTED = "lab.started"
    LAB_COMPLETED = "lab.completed"

    # Dead letter queue
    DLQ = "dlq.events"


@dataclass
class KafkaMessage:
    """Structured Kafka message with metadata."""
    topic: str
    event_type: str
    payload: dict[str, Any]
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    version: str = "1.0"
    source_service: str = "ai-learning-platform"

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "version": self.version,
            "source_service": self.source_service,
        }

    def serialize(self) -> bytes:
        return json.dumps(self.to_dict()).encode("utf-8")


class KafkaManager:
    """Manages Kafka producer and consumer connections."""

    def __init__(self) -> None:
        self._producer: AIOKafkaProducer | None = None
        self._consumers: dict[str, AIOKafkaConsumer] = {}
        self._handlers: dict[str, list[Callable]] = {}

    async def connect(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            compression_type="gzip",
            max_batch_size=16384,
            linger_ms=10,
            acks="all",
        )
        await self._producer.start()
        log.info("Kafka producer connected", servers=settings.KAFKA_BOOTSTRAP_SERVERS)

    async def disconnect(self) -> None:
        if self._producer:
            await self._producer.stop()
        for consumer in self._consumers.values():
            await consumer.stop()
        log.info("Kafka disconnected")

    async def health_check(self) -> bool:
        try:
            return self._producer is not None and self._producer._closed is False
        except Exception:
            return False

    async def publish(
        self,
        topic: str,
        event_type: str,
        payload: dict[str, Any],
        key: str | None = None,
    ) -> None:
        """Publish a structured event to a Kafka topic."""
        message = KafkaMessage(topic=topic, event_type=event_type, payload=payload)
        try:
            await self._producer.send_and_wait(
                topic,
                value=message.to_dict(),
                key=key,
            )
            log.debug("Kafka event published", topic=topic, event_type=event_type)
        except KafkaError as e:
            log.error("Failed to publish Kafka event", topic=topic, error=str(e))
            await self._send_to_dlq(message, error=str(e))
            raise

    async def _send_to_dlq(self, message: KafkaMessage, error: str) -> None:
        try:
            dlq_payload = {"original_message": message.to_dict(), "error": error}
            await self._producer.send(Topics.DLQ, value=dlq_payload)
        except Exception:
            log.exception("Failed to send to DLQ")

    def create_consumer(
        self,
        topics: list[str],
        group_id: str | None = None,
    ) -> AIOKafkaConsumer:
        return AIOKafkaConsumer(
            *topics,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=group_id or settings.KAFKA_CONSUMER_GROUP,
            auto_offset_reset=settings.KAFKA_AUTO_OFFSET_RESET,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            enable_auto_commit=False,
            max_poll_records=100,
        )


kafka_manager = KafkaManager()
