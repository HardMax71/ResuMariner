import logging

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.metrics import REQUEST_DURATION

from .serializers import (
    UpsertResumeRequestSerializer,
    VectorStoreRequestSerializer,
)
from .services.graph_db_service import GraphDBService
from .services.vector_db_service import VectorDBService

logger = logging.getLogger(__name__)


class UpsertResumeView(APIView):
    def post(self, request: Request) -> Response:
        with REQUEST_DURATION.labels(method="POST", endpoint="/storage/resume").time():
            serializer = UpsertResumeRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            svc = GraphDBService()
            resume = data["resume_data"]
            success = svc.upsert_resume(resume)

            if not success:
                return Response(
                    {"error": "Failed to store resume in Neo4j"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            resp = {"graph_id": resume.uid or "unknown"}
            return Response(resp, status=status.HTTP_200_OK)


class GetResumeView(APIView):
    def get(self, request: Request, resume_id: str) -> Response:
        with REQUEST_DURATION.labels(method="GET", endpoint="/storage/resume/{id}").time():
            svc = GraphDBService()
            resumes = svc.get_resumes([resume_id])
            if not resumes or resume_id not in resumes:
                return Response({"detail": "Resume not found"}, status=status.HTTP_404_NOT_FOUND)
            resume_dict = resumes[resume_id].model_dump(exclude_none=True, mode="json")
            return Response(resume_dict)


class StoreVectorsView(APIView):
    def post(self, request: Request) -> Response:
        with REQUEST_DURATION.labels(method="POST", endpoint="/storage/vectors").time():
            serializer = VectorStoreRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            vsvc = VectorDBService()
            ids = vsvc.store_vectors(data["resume_id"], data["vectors"])
            out = {"status": "success", "vector_count": len(ids)}
            return Response(out, status=status.HTTP_200_OK)


class DeleteResumeView(APIView):
    def delete(self, request: Request, resume_id: str) -> Response:
        with REQUEST_DURATION.labels(method="DELETE", endpoint="/storage/resume/{id}/delete").time():
            gsvc = GraphDBService()
            gsvc.delete_resume(resume_id=resume_id)
            vsvc = VectorDBService()
            vsvc.delete_resume_vectors(resume_id)
            return Response({"status": "success", "message": f"Resume {resume_id} deleted successfully"})
