import asyncio
import atexit
import logging
import time

from django.http import HttpRequest, HttpResponse

from core.database import create_graph_service, create_vector_service
from core.metrics import REQUEST_COUNT, REQUEST_DURATION
from processor.services.job_service import JobService
from processor.services.resume_service import ResumeService
from search.services.search_coordinator import SearchCoordinator

logger = logging.getLogger(__name__)


class PrometheusMiddleware:
    """Async middleware for Prometheus metrics collection."""

    sync_capable = False
    async_capable = True

    def __init__(self, get_response):
        self.get_response = get_response

    async def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.path == "/metrics":
            return await self.get_response(request)  # type: ignore[no-any-return]

        start_time = time.time()
        response = await self.get_response(request)
        duration = time.time() - start_time

        endpoint = self._normalize_path(request.path)
        method = request.method

        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=response.status_code).inc()

        return response  # type: ignore[no-any-return]

    def _normalize_path(self, path: str) -> str:
        path = path.rstrip("/") or "/"
        if len(path) > 100:
            path = path[:100] + "..."
        return path


class DatabaseServicesMiddleware:
    """Async middleware for database services initialization and injection."""

    sync_capable = False
    async_capable = True

    _initialization_lock = asyncio.Lock()
    _job_service = None
    _resume_service = None

    def __init__(self, get_response):
        self.get_response = get_response
        self.graph_db = create_graph_service()
        self.vector_db = create_vector_service()
        logger.info("Database services initialized")

    async def __call__(self, request: HttpRequest) -> HttpResponse:
        if DatabaseServicesMiddleware._job_service is None:
            async with DatabaseServicesMiddleware._initialization_lock:
                if DatabaseServicesMiddleware._job_service is None:
                    await JobService.initialize()
                    DatabaseServicesMiddleware._job_service = JobService()
                    DatabaseServicesMiddleware._resume_service = ResumeService(
                        DatabaseServicesMiddleware._job_service, self.graph_db, self.vector_db
                    )
                    logger.info("JobService and ResumeService singletons initialized")

        request.graph_db = self.graph_db  # type: ignore[attr-defined]
        request.vector_db = self.vector_db  # type: ignore[attr-defined]
        request.job_service = DatabaseServicesMiddleware._job_service  # type: ignore[attr-defined]
        request.resume_service = DatabaseServicesMiddleware._resume_service  # type: ignore[attr-defined]

        response = await self.get_response(request)
        return response  # type: ignore[no-any-return]


class SearchServicesMiddleware:
    """Async middleware for search services initialization and injection."""

    sync_capable = False
    async_capable = True

    _initialization_lock = asyncio.Lock()
    _search_coordinator = None
    _cleanup_registered = False

    def __init__(self, get_response):
        self.get_response = get_response

    async def __call__(self, request: HttpRequest) -> HttpResponse:
        if SearchServicesMiddleware._search_coordinator is None:
            async with SearchServicesMiddleware._initialization_lock:
                if SearchServicesMiddleware._search_coordinator is None:
                    SearchServicesMiddleware._search_coordinator = SearchCoordinator()
                    logger.info("SearchCoordinator singleton initialized")

                    if not SearchServicesMiddleware._cleanup_registered:
                        atexit.register(SearchServicesMiddleware._cleanup)
                        SearchServicesMiddleware._cleanup_registered = True
                        logger.info("SearchCoordinator cleanup registered")

        request.search_coordinator = SearchServicesMiddleware._search_coordinator  # type: ignore[attr-defined]

        response = await self.get_response(request)
        return response  # type: ignore[no-any-return]

    @staticmethod
    def _cleanup() -> None:
        """Cleanup function called on process shutdown."""
        if SearchServicesMiddleware._search_coordinator is not None:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(SearchServicesMiddleware._search_coordinator.close())
                else:
                    loop.run_until_complete(SearchServicesMiddleware._search_coordinator.close())
            except Exception as e:
                logger.error("Error closing SearchCoordinator: %s", e)
