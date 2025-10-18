import asyncio
import logging
import time
from collections.abc import Awaitable, Callable

from django.http import HttpRequest, HttpResponse

from core.database import create_graph_service, create_vector_service
from core.metrics import REQUEST_COUNT, REQUEST_DURATION
from processor.services.job_service import JobService
from processor.services.resume_service import ResumeService
from rag.services.rag_service import RAGService
from search.services.search_coordinator import SearchCoordinator

logger = logging.getLogger(__name__)


class PrometheusMiddleware:
    """Async middleware for Prometheus metrics collection."""

    sync_capable = False
    async_capable = True

    def __init__(self, get_response: Callable[[HttpRequest], Awaitable[HttpResponse]]):
        self.get_response = get_response

    async def __call__(self, request: HttpRequest) -> HttpResponse:
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
    """Async middleware for database services initialization and injection."""

    sync_capable = False
    async_capable = True

    _initialization_lock = asyncio.Lock()
    _graph_db = None
    _vector_db = None
    _job_service = None
    _resume_service = None
    _rag_service = None

    def __init__(self, get_response: Callable[[HttpRequest], Awaitable[HttpResponse]]):
        self.get_response = get_response

    async def __call__(self, request: HttpRequest) -> HttpResponse:
        if DatabaseServicesMiddleware._job_service is None:
            async with DatabaseServicesMiddleware._initialization_lock:
                if DatabaseServicesMiddleware._job_service is None:
                    graph_db = create_graph_service()
                    vector_db = create_vector_service()
                    await JobService.initialize()
                    job_service = JobService()
                    resume_service = ResumeService(job_service, graph_db, vector_db)
                    rag_service = RAGService(graph_db, vector_db)

                    DatabaseServicesMiddleware._graph_db = graph_db
                    DatabaseServicesMiddleware._vector_db = vector_db
                    DatabaseServicesMiddleware._job_service = job_service
                    DatabaseServicesMiddleware._resume_service = resume_service
                    DatabaseServicesMiddleware._rag_service = rag_service
                    logger.info("Database services initialized")

        request.graph_db = DatabaseServicesMiddleware._graph_db  # type: ignore[attr-defined]
        request.vector_db = DatabaseServicesMiddleware._vector_db  # type: ignore[attr-defined]
        request.job_service = DatabaseServicesMiddleware._job_service  # type: ignore[attr-defined]
        request.resume_service = DatabaseServicesMiddleware._resume_service  # type: ignore[attr-defined]
        request.rag_service = DatabaseServicesMiddleware._rag_service  # type: ignore[attr-defined]

        response = await self.get_response(request)
        return response


class SearchServicesMiddleware:
    """Async middleware for search services initialization and injection."""

    sync_capable = False
    async_capable = True

    _initialization_lock = asyncio.Lock()
    _search_coordinator = None

    def __init__(self, get_response: Callable[[HttpRequest], Awaitable[HttpResponse]]):
        self.get_response = get_response

    async def __call__(self, request: HttpRequest) -> HttpResponse:
        if SearchServicesMiddleware._search_coordinator is None:
            async with SearchServicesMiddleware._initialization_lock:
                if SearchServicesMiddleware._search_coordinator is None:
                    SearchServicesMiddleware._search_coordinator = SearchCoordinator()
                    logger.info("SearchCoordinator singleton initialized")

        request.search_coordinator = SearchServicesMiddleware._search_coordinator  # type: ignore[attr-defined]

        response = await self.get_response(request)
        return response
