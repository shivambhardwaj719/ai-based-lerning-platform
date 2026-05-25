"""
OpenTelemetry setup for distributed tracing and metrics.
Sends traces to Jaeger via OTLP gRPC (Jaeger 1.35+ supports OTLP natively).
"""
from __future__ import annotations

import structlog
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

from core.config import settings

log = structlog.get_logger()


def setup_telemetry() -> None:
    resource = Resource(attributes={SERVICE_NAME: settings.APP_NAME})
    sampler = TraceIdRatioBased(1.0 if settings.is_development else 0.1)
    provider = TracerProvider(resource=resource, sampler=sampler)

    # Send traces to Jaeger via OTLP gRPC (port 4317)
    try:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        otlp_endpoint = f"http://{settings.JAEGER_HOST}:4317"
        otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        log.info("Telemetry: OTLP exporter configured", endpoint=otlp_endpoint)
    except Exception as exc:
        log.warning("Telemetry: OTLP exporter unavailable, skipping trace export", error=str(exc))

    trace.set_tracer_provider(provider)

    # Auto-instrument key libraries
    FastAPIInstrumentor().instrument()
    RedisInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument()
