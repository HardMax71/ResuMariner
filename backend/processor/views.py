import logging

from adrf.views import APIView
from django.conf import settings
from django.core.cache import cache as django_cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.extensions import OpenApiSerializerExtension
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import serializers, status
from rest_framework.exceptions import NotFound
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.request import Request
from rest_framework.response import Response

from core.domain.processing import ResumeResponse
from core.file_types import FILE_TYPE_REGISTRY

from .serializers import FileUploadSerializer

logger = logging.getLogger(__name__)

THROTTLE_RATES: dict[str, str] = settings.REST_FRAMEWORK.get("DEFAULT_THROTTLE_RATES", {})  # type: ignore[assignment]


class QueueMetricsSerializer(serializers.Serializer):
    stream_length = serializers.IntegerField(help_text="Total items in Redis stream")
    queue_length = serializers.IntegerField(help_text="Pending items in queue")
    scheduled_retries = serializers.IntegerField(help_text="Items scheduled for retry")
    active_jobs = serializers.IntegerField(help_text="Currently processing jobs")
    redis_memory_usage = serializers.IntegerField(help_text="Redis memory usage in bytes")


class ProcessingConfigSerializer(serializers.Serializer):
    text_llm_provider = serializers.CharField(help_text="LLM provider for text extraction")
    text_llm_model = serializers.CharField(help_text="LLM model for text extraction")
    ocr_llm_provider = serializers.CharField(help_text="LLM provider for OCR")
    ocr_llm_model = serializers.CharField(help_text="LLM model for OCR")
    generate_review = serializers.BooleanField(help_text="Whether AI review is enabled")
    store_in_db = serializers.BooleanField(help_text="Whether to store in database")


class HealthResponseSerializer(serializers.Serializer):
    status = serializers.CharField(help_text="Service status: ok, degraded, or down")
    service = serializers.CharField(help_text="Service name")
    queue = QueueMetricsSerializer()
    processing_config = ProcessingConfigSerializer()


class FileTypeConfigSerializer(serializers.Serializer):
    """Configuration for a single file type."""

    media_type = serializers.CharField(help_text="MIME type")
    category = serializers.CharField(help_text="File category (document, image, etc)")
    max_size_mb = serializers.IntegerField(help_text="Maximum file size in MB")
    parser = serializers.CharField(help_text="Parser used for this file type")


class FileConfigResponseSerializer(serializers.Serializer):
    """Dictionary of file type configurations keyed by extension."""

    def to_representation(self, instance: dict) -> dict:
        """Return the dict as-is since keys are dynamic extensions."""
        return instance


class FileConfigResponseExtension(OpenApiSerializerExtension):
    """Extension to generate proper additionalProperties schema for FileConfigResponse."""

    target_class = "processor.views.FileConfigResponseSerializer"

    def map_serializer(self, auto_schema, direction):
        """Generate object schema with additionalProperties pointing to FileTypeConfig."""
        return {
            "type": "object",
            "additionalProperties": auto_schema.resolve_serializer(FileTypeConfigSerializer, direction).ref,
        }


class ResumeListResponse(serializers.Serializer):
    count = serializers.IntegerField(help_text="Total number of resumes")
    next = serializers.CharField(allow_null=True, help_text="Next page URL")
    previous = serializers.CharField(allow_null=True, help_text="Previous page URL")
    results = serializers.ListField(help_text="Resumes for current page")


class ResumeCollectionView(APIView):
    """List and upload resume endpoints."""

    pagination_class = LimitOffsetPagination
    throttle_scope = "upload"

    @extend_schema(
        parameters=[
            OpenApiParameter(name="limit", type=int, description="Number of results per page", required=False),
            OpenApiParameter(name="offset", type=int, description="Starting index", required=False),
        ],
        responses={200: ResumeListResponse},
        description="List all resumes with pagination.",
    )
    async def get(self, request: Request) -> Response:
        paginator = self.pagination_class()

        limit = paginator.get_limit(request)
        offset = paginator.get_offset(request)
        total_count = await request.job_service.count_jobs()

        jobs = await request.job_service.list_jobs(limit=limit, offset=offset)
        jobs_data = [job.model_dump(exclude={"file_path"}) for job in jobs]

        paginator.count = total_count
        paginator.limit = limit
        paginator.offset = offset
        paginator.request = request

        return paginator.get_paginated_response(jobs_data)

    @extend_schema(
        request=FileUploadSerializer,
        responses={
            202: ResumeResponse,
            400: OpenApiResponse(description="Invalid file or resume already exists"),
            429: OpenApiResponse(description=f"Rate limit exceeded ({THROTTLE_RATES.get('upload', 'N/A')})"),
        },
        description="Upload a resume file for processing. Supported formats available at /api/v1/config/file-types/. Returns resume ID for tracking.",
    )
    async def post(self, request: Request) -> Response:
        serializer = FileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data["file"]
        file_content = file.read()

        job = await request.resume_service.upload_resume(file_content, file.name)

        return Response(job.model_dump(exclude={"file_path"}), status=status.HTTP_202_ACCEPTED)


class ResumeDetailView(APIView):
    """Get and delete resume by ID endpoints."""

    @extend_schema(
        responses={
            200: ResumeResponse,
            404: OpenApiResponse(description="Resume not found"),
        },
        description="Get resume by ID. Returns status and full data if completed.",
    )
    async def get(self, request: Request, uid: str) -> Response:
        job = await request.job_service.get_job(uid)
        return Response(job.model_dump(exclude={"file_path"}))

    @extend_schema(
        responses={
            204: OpenApiResponse(description="Resume deleted successfully"),
            404: OpenApiResponse(description="Resume not found"),
        },
        description="Delete resume and all associated data (vectors, files). Preserves shared entities.",
    )
    async def delete(self, request: Request, uid: str) -> Response:
        # Check if job exists before deleting
        await request.job_service.get_job(uid)  # Raises NotFound if not exists
        await request.resume_service.delete_resume(uid)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResumeByEmailView(APIView):
    """Delete resume by email endpoint."""

    @extend_schema(
        responses={
            204: OpenApiResponse(description="Resume deleted successfully"),
            404: OpenApiResponse(description="Resume not found"),
        },
        description="Delete resume by email address.",
    )
    async def delete(self, request: Request, email: str) -> Response:
        uid = await request.graph_db.get_resume_uid_by_email(email.lower())
        if not uid:
            logger.warning("Resume delete failed: email %s not found", email)
            raise NotFound("Resume not found")

        await request.resume_service.delete_resume(uid)
        return Response(status=status.HTTP_204_NO_CONTENT)


class HealthView(APIView):
    """Service health status endpoint."""

    @extend_schema(
        responses={200: HealthResponseSerializer},
        description="Get service health status. Returns system status, queue statistics, and processing configuration.",
    )
    async def get(self, request: Request) -> Response:
        health_data = {
            "status": "ok",
            "service": "resume-processing-api",
            "queue": await request.job_service.get_queue_stats(),
            "processing_config": {
                "text_llm_provider": settings.TEXT_LLM_PROVIDER,
                "text_llm_model": settings.TEXT_LLM_MODEL,
                "ocr_llm_provider": settings.OCR_LLM_PROVIDER,
                "ocr_llm_model": settings.OCR_LLM_MODEL,
                "generate_review": settings.WORKER_GENERATE_REVIEW,
                "store_in_db": settings.WORKER_STORE_IN_DB,
            },
        }
        return Response(health_data, status=status.HTTP_200_OK)


class FileConfigView(APIView):
    """File upload configuration endpoint."""

    @extend_schema(
        responses={200: FileConfigResponseSerializer},
        description="Get file upload configuration. Returns allowed extensions, MIME types, max sizes, and categories. Keys are file extensions.",
    )
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request: Request) -> Response:
        cache_key = "file_config_v1"
        cached = django_cache.get(cache_key)
        if cached:
            return Response(cached, status=status.HTTP_200_OK)

        config = {
            ext: {
                "media_type": spec["media_type"],
                "category": spec["category"],
                "max_size_mb": spec["max_size_mb"],
                "parser": spec["parser"],
            }
            for ext, spec in FILE_TYPE_REGISTRY.items()
        }

        django_cache.set(cache_key, config, 60 * 60 * 24)
        return Response(config, status=status.HTTP_200_OK)
