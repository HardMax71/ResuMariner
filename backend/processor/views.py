import logging
import uuid

from adrf.views import APIView
from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import FileUploadSerializer, JobResponseSerializer, JobStatus
from .services.cleanup_service import CleanupService
from .services.file_service import FileService
from .services.job_service import JobService
from .utils.redis_queue import RedisJobQueue

logger = logging.getLogger(__name__)


class UploadCVView(APIView):
    @extend_schema(
        request=FileUploadSerializer,
        responses={202: JobResponseSerializer},
        description="Upload a resume file for processing. Accepts PDF, DOCX, DOC, TXT formats. Returns a job ID for tracking.",
    )
    async def post(self, request: Request) -> Response:
        serializer = FileUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        file = serializer.validated_data["file"]
        job_id = str(uuid.uuid4())

        try:
            file.seek(0)
            temp_path = await FileService.save_validated_content(file.read(), file.name, job_id)

            service = JobService()
            job = await service.create_job(temp_path)
            _ = await service.process_job(job.job_id)

            response_data = JobResponseSerializer(job.model_dump()).data
            return Response(response_data, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JobStatusView(APIView):
    @extend_schema(
        responses={200: JobResponseSerializer},
        description="Get the status of a processing job. Returns job status (pending, processing, completed, failed) and result URL if completed.",
    )
    async def get(self, request, job_id):
        service = JobService()
        job = await service.get_job(job_id)
        if not job:
            return Response({"detail": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        # Add result_url to response
        job_data = job.model_dump()
        if job.status == JobStatus.COMPLETED:
            job_data["result_url"] = request.build_absolute_uri(f"/api/v1/jobs/{job_id}/result/")

        serializer = JobResponseSerializer(job_data)
        return Response(serializer.data)


class JobResultView(APIView):
    @extend_schema(
        responses={200: OpenApiResponse(description="Job result containing resume data, review, and metadata")},
        description="Get the result of a completed job. Returns structured resume data, review feedback, and processing metadata.",
    )
    async def get(self, request, job_id):
        service = JobService()
        job = await service.get_job(job_id)
        if not job:
            return Response({"detail": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        if job.status != JobStatus.COMPLETED:
            return Response({"detail": "Job not completed yet"}, status=status.HTTP_400_BAD_REQUEST)

        if not job.result:
            return Response({"detail": "No result data available"}, status=status.HTTP_404_NOT_FOUND)

        return Response(job.result)


class CleanupJobsView(APIView):
    @extend_schema(
        request={"application/json": {"type": "object", "properties": {"days": {"type": "integer"}, "force": {"type": "boolean"}}}},
        responses={200: OpenApiResponse(description="Cleanup result with deleted count")},
        description="Cleanup old jobs. Deletes jobs older than specified days. Use force=true to delete all jobs.",
    )
    async def post(self, request: Request) -> Response:
        days = request.data.get("days", settings.JOB_RETENTION_DAYS)
        force = request.data.get("force", False)

        cleanup = CleanupService()
        deleted_count = await cleanup.cleanup_old_jobs(days=days, force=force)

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
