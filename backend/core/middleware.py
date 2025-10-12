import logging
import time
from collections.abc import Awaitable, Callable

import redis.asyncio as redis
from django.conf import settings
from django.http import HttpRequest, HttpResponse

from core.database import create_graph_service, create_vector_service
from core.metrics import REQUEST_COUNT, REQUEST_DURATION

logger = logging.getLogger(__name__)


class PrometheusMiddleware:
    sync_capable = False
    async_capable = True

    def __init__(self, get_response):
        self.get_response = get_response

    async def __call__(self, request):
        if request.path == "/metrics":
            return await self.get_response(request)

        start_time = time.time()
        response = await self.get_response(request)
        duration = time.time() - start_time

        endpoint = self._normalize_path(request.path)
        method = request.method

        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=response.status_code).inc()

        return response

    def _normalize_path(self, path: str) -> str:
        path = path.rstrip("/") or "/"
        if len(path) > 100:
            path = path[:100] + "..."
        return path


class DatabaseServicesMiddleware:
    sync_capable = False
    async_capable = True

    def __init__(self, get_response: Callable[[HttpRequest], Awaitable[HttpResponse]]):
        self.get_response = get_response
        self.graph_db = create_graph_service()
        self.vector_db = create_vector_service()
        self.redis_pool = redis.ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
            max_connections=50,
        )
        logger.info("Database services initialized (singleton instances)")

    async def __call__(self, request: HttpRequest) -> HttpResponse:
        request.graph_db = self.graph_db  # type: ignore[attr-defined]
        request.vector_db = self.vector_db  # type: ignore[attr-defined]
        request.redis = redis.Redis(connection_pool=self.redis_pool)  # type: ignore[attr-defined]

        response = await self.get_response(request)
        return response
