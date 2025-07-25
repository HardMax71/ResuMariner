import logging
import time
from contextlib import contextmanager
from typing import Optional, Dict, Any
from functools import wraps

from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest
from prometheus_client.core import CollectorRegistry

logger = logging.getLogger(__name__)

# Global metrics registry
registry = CollectorRegistry()

# Prometheus metrics
REQUEST_COUNT = Counter(
    "requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code", "service"],
    registry=registry,
)

REQUEST_DURATION = Histogram(
    "request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint", "service"],
    registry=registry,
)

ACTIVE_CONNECTIONS = Gauge(
    "active_connections",
    "Number of active connections",
    ["service", "connection_type"],
    registry=registry,
)

JOB_METRICS = Counter(
    "jobs_total",
    "Total jobs processed",
    ["service", "status", "job_type"],
    registry=registry,
)

JOB_PROCESSING_TIME = Histogram(
    "job_processing_seconds",
    "Job processing time in seconds",
    ["service", "job_type"],
    registry=registry,
)

QUEUE_SIZE = Gauge(
    "queue_size", "Current queue size", ["service", "queue_name"], registry=registry
)

ERROR_COUNT = Counter(
    "errors_total",
    "Total errors",
    ["service", "error_type", "endpoint"],
    registry=registry,
)

SERVICE_INFO = Info("service_info", "Service information", registry=registry)

# OpenTelemetry components
tracer_provider: Optional[TracerProvider] = None
tracer: Optional[trace.Tracer] = None
meter_provider: Optional[MeterProvider] = None


def setup_tracing(
    service_name: str, jaeger_host: str = "jaeger", jaeger_port: int = 6831
):
    """Setup OpenTelemetry tracing with Jaeger"""
    global tracer_provider, tracer

    try:
        # Setup tracer provider
        tracer_provider = TracerProvider(
            resource=Resource.create(
                {"service.name": service_name, "service.version": "1.0.0"}
            )
        )

        # Setup Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name=jaeger_host,
            agent_port=jaeger_port,
        )

        # Setup span processor
        span_processor = BatchSpanProcessor(jaeger_exporter)
        tracer_provider.add_span_processor(span_processor)

        # Set global tracer provider
        trace.set_tracer_provider(tracer_provider)
        tracer = trace.get_tracer(__name__)

        logger.info(f"OpenTelemetry tracing initialized for service: {service_name}")

    except Exception as e:
        logger.error(f"Failed to setup tracing: {str(e)}")


def setup_metrics(service_name: str):
    """Setup OpenTelemetry metrics with Prometheus"""
    global meter_provider

    try:
        # Setup Prometheus metric reader
        prometheus_reader = PrometheusMetricReader()

        # Setup meter provider
        meter_provider = MeterProvider(
            metric_readers=[prometheus_reader],
            resource=Resource.create(
                {"service.name": service_name, "service.version": "1.0.0"}
            ),
        )

        # Set global meter provider
        metrics.set_meter_provider(meter_provider)

        # Set service info
        SERVICE_INFO.info({"name": service_name, "version": "1.0.0"})

        logger.info(f"OpenTelemetry metrics initialized for service: {service_name}")

    except Exception as e:
        logger.error(f"Failed to setup metrics: {str(e)}")


def setup_instrumentation(app, service_name: str):
    """Setup automatic instrumentation for FastAPI, HTTPX, and Redis"""
    try:
        # Instrument FastAPI
        FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)

        # Instrument HTTPX
        HTTPXClientInstrumentor().instrument(tracer_provider=tracer_provider)

        # Instrument Redis
        RedisInstrumentor().instrument(tracer_provider=tracer_provider)

        logger.info(f"Automatic instrumentation enabled for {service_name}")

    except Exception as e:
        logger.error(f"Failed to setup instrumentation: {str(e)}")


def init_monitoring(
    app, service_name: str, jaeger_host: str = "jaeger", jaeger_port: int = 6831
):
    """Initialize complete monitoring setup"""
    try:
        # Setup tracing
        setup_tracing(service_name, jaeger_host, jaeger_port)

        # Setup metrics
        setup_metrics(service_name)

        # Setup instrumentation
        setup_instrumentation(app, service_name)

        logger.info(f"Complete monitoring setup initialized for {service_name}")

    except Exception as e:
        logger.error(f"Failed to initialize monitoring: {str(e)}")


def get_metrics():
    """Get Prometheus metrics"""
    return generate_latest(registry).decode("utf-8")


@contextmanager
def trace_span(name: str, attributes: Optional[Dict[str, Any]] = None):
    """Context manager for creating spans"""
    if tracer is None:
        yield None
        return

    with tracer.start_as_current_span(name) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        yield span


def trace_function(
    span_name: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None
):
    """Decorator for tracing functions"""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            name = span_name or f"{func.__module__}.{func.__name__}"
            with trace_span(name, attributes) as span:
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    if span:
                        span.set_attribute("function.success", True)
                    return result
                except Exception as e:
                    if span:
                        span.set_attribute("function.success", False)
                        span.set_attribute("function.error", str(e))
                    raise
                finally:
                    duration = time.time() - start_time
                    if span:
                        span.set_attribute("function.duration", duration)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            name = span_name or f"{func.__module__}.{func.__name__}"
            with trace_span(name, attributes) as span:
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    if span:
                        span.set_attribute("function.success", True)
                    return result
                except Exception as e:
                    if span:
                        span.set_attribute("function.success", False)
                        span.set_attribute("function.error", str(e))
                    raise
                finally:
                    duration = time.time() - start_time
                    if span:
                        span.set_attribute("function.duration", duration)

        return (
            async_wrapper
            if hasattr(func, "__code__") and func.__code__.co_flags & 0x80
            else sync_wrapper
        )

    return decorator


def record_request_metrics(
    method: str, endpoint: str, status_code: int, service: str, duration: float
):
    """Record HTTP request metrics"""
    REQUEST_COUNT.labels(
        method=method, endpoint=endpoint, status_code=status_code, service=service
    ).inc()
    REQUEST_DURATION.labels(method=method, endpoint=endpoint, service=service).observe(
        duration
    )


def record_job_metrics(
    service: str, status: str, job_type: str, processing_time: Optional[float] = None
):
    """Record job processing metrics"""
    JOB_METRICS.labels(service=service, status=status, job_type=job_type).inc()
    if processing_time is not None:
        JOB_PROCESSING_TIME.labels(service=service, job_type=job_type).observe(
            processing_time
        )


def record_error_metrics(service: str, error_type: str, endpoint: str):
    """Record error metrics"""
    ERROR_COUNT.labels(service=service, error_type=error_type, endpoint=endpoint).inc()


def update_queue_size(service: str, queue_name: str, size: int):
    """Update queue size metric"""
    QUEUE_SIZE.labels(service=service, queue_name=queue_name).set(size)


def update_connection_count(service: str, connection_type: str, count: int):
    """Update active connection count"""
    ACTIVE_CONNECTIONS.labels(service=service, connection_type=connection_type).set(
        count
    )


class MetricsMiddleware:
    """FastAPI middleware for automatic metrics collection"""

    def __init__(self, app, service_name: str):
        self.app = app
        self.service_name = service_name

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()
        method = scope["method"]
        path = scope["path"]

        # Wrap send to capture status code
        status_code = 500

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            record_error_metrics(self.service_name, type(e).__name__, path)
            raise
        finally:
            duration = time.time() - start_time
            record_request_metrics(
                method, path, status_code, self.service_name, duration
            )
