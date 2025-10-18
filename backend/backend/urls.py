from typing import Any

from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from core.metrics import update_queue_metrics
from processor.services.job_service import JobService


async def metrics_view(_request: Any) -> HttpResponse:
    try:
        job_service = JobService()
        stats = await job_service.get_queue_stats()
        update_queue_metrics(stats)
    except Exception:
        pass

    return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)


urlpatterns = [
    path("admin/", admin.site.urls),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # API v1 endpoints
    path("api/v1/", include("search.urls")),
    path("api/v1/", include("processor.urls")),
    path("api/v1/rag/", include("rag.urls")),
    # Metrics (Prometheus format)
    path("metrics", metrics_view),
]
