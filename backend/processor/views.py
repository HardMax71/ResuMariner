import logging

from adrf.views import APIView
from django.conf import settings
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from core.file_types import FILE_TYPE_REGISTRY

from .serializers import CleanupSerializer, FileUploadSerializer, JobStatus, ResumeResponseSerializer
from .services.cleanup_service import CleanupService
from .services.job_service import JobService
from .utils.redis_queue import RedisJobQueue

logger = logging.getLogger(__name__)


class ResumeCollectionView(APIView):
    @extend_schema(
        responses={200: OpenApiResponse(description="List of all resumes with their processing status")},
        description="List all resumes in the system.",
    )
    async def get(self, request: Request) -> Response:
        service = JobService()
        jobs = await service.list_jobs(limit=100)

        jobs_data = []
        for job in jobs:
            job_dict = job.model_dump(mode="json")
            jobs_data.append(job_dict)

        return Response({"count": len(jobs_data), "resumes": jobs_data})

    @extend_schema(
        request=FileUploadSerializer,
        responses={202: ResumeResponseSerializer},
        description="Upload a resume file for processing. Supported formats available at /api/v1/config/file-types/. Returns resume ID for tracking.",
    )
    async def post(self, request: Request) -> Response:
        serializer = FileUploadSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"File upload validation failed: {serializer.errors}")
            return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        file = serializer.validated_data["file"]
        file_content = file.read()

        try:
            service = JobService()
            result = await service.upload_resume(file_content, file.name, request.graph_db)

            if "error" in result:
                return Response({"detail": result["error"]}, status=status.HTTP_400_BAD_REQUEST)

            if result.get("existing"):
                return Response({"uid": result["uid"], "message": "Resume already exists"}, status=status.HTTP_200_OK)

            job_data = result["job"].model_dump()
            response_data = ResumeResponseSerializer(job_data).data
            return Response(response_data, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            logger.error("Upload failed: %s", e)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResumeDetailView(APIView):
    @extend_schema(
        responses={200: OpenApiResponse(description="Resume data with processing status")},
        description="Get resume by ID. Returns status and full data if completed.",
    )
    async def get(self, request, uid):
        service = JobService()
        job = await service.get_job(uid)
        if not job:
            return Response({"detail": "Resume not found"}, status=status.HTTP_404_NOT_FOUND)

        response_data = {
            "uid": job.uid,
            "status": job.status,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
        }

        if job.status == JobStatus.COMPLETED:
            if job.result:
                response_data["data"] = job.result
        elif job.status == JobStatus.FAILED:
            response_data["error"] = job.error

        return Response(response_data)

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Deletion result"),
            404: OpenApiResponse(description="Resume not found"),
        },
        description="Delete resume and all associated data (vectors, files). Preserves shared entities.",
    )
    async def delete(self, request, uid):
        service = JobService()
        result = await service.delete_job_complete(uid, request.graph_db, request.vector_db)

        if result["errors"] and not result["job_deleted"]:
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        return Response(result, status=status.HTTP_200_OK)


class ResumeByEmailView(APIView):
    @extend_schema(
        responses={
            200: OpenApiResponse(description="Resume deleted successfully"),
            404: OpenApiResponse(description="Resume not found"),
        },
        description="Delete resume by email address.",
    )
    async def delete(self, request, email: str):
        existing = await request.graph_db.get_resume_by_email(email.lower())
        if not existing:
            return Response({"detail": "Resume not found"}, status=status.HTTP_404_NOT_FOUND)

        service = JobService()
        result = await service.delete_job_complete(existing.uid, request.graph_db, request.vector_db)

        if result["errors"] and not result["job_deleted"]:
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        return Response(result, status=status.HTTP_200_OK)


class CleanupResumesView(APIView):
    @extend_schema(
        request=CleanupSerializer,
        responses={200: OpenApiResponse(description="Cleanup result with deleted count")},
        description="Cleanup old resumes. Deletes resumes older than specified days. Use force=true to delete all.",
    )
    async def post(self, request: Request) -> Response:
        serializer = CleanupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        days = validated_data.get("days", settings.JOB_RETENTION_DAYS)
        force = validated_data.get("force", False)

        cleanup = CleanupService()
        deleted_count = await cleanup.cleanup_old_jobs(days, request.graph_db, request.vector_db, force=force)

        return Response(
            {"status": "success", "deleted_count": deleted_count, "retention_days": days}, status=status.HTTP_200_OK
        )


class HealthView(APIView):
    @extend_schema(
        responses={200: OpenApiResponse(description="Health status including queue stats and configuration")},
        description="Get service health status. Returns system status, queue statistics, and processing configuration.",
    )
    async def get(self, request):
        queue = RedisJobQueue()

        health_data = {
            "status": "ok",
            "service": "resume-processing-api",
            "queue": await queue.get_queue_stats(),
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
    @extend_schema(
        responses={200: OpenApiResponse(description="File upload configuration")},
        description="Get file upload configuration. Returns allowed extensions, MIME types, max sizes, and categories.",
    )
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        cache_key = "file_config_v1"
        cached = cache.get(cache_key)
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

        cache.set(cache_key, config, 60 * 60 * 24)
        return Response(config, status=status.HTTP_200_OK)
