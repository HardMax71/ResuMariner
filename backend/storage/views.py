import logging

from adrf.views import APIView
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from storage.serializers import UpsertResumeRequestSerializer, VectorStoreRequestSerializer
from storage.services.graph_db_service import GraphDBService
from storage.services.vector_db_service import VectorDBService

logger = logging.getLogger(__name__)


class UpsertResumeView(APIView):
    async def post(self, request: Request) -> Response:
        serializer = UpsertResumeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        graph_db = await GraphDBService.get_instance()

        resume = data["resume_data"]
        success = await graph_db.upsert_resume(resume)

        if not success:
            return Response({"error": "Failed to store resume in Neo4j"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"graph_id": resume.uid or "unknown"}, status=status.HTTP_200_OK)


class GetResumeView(APIView):
    async def get(self, request: Request, resume_id: str) -> Response:
        graph_db = await GraphDBService.get_instance()

        resumes = await graph_db.get_resumes([resume_id])
        if not resumes or resume_id not in resumes:
            return Response({"detail": "Resume not found"}, status=status.HTTP_404_NOT_FOUND)

        resume_dict = resumes[resume_id].model_dump(exclude_none=True, mode="json")
        return Response(resume_dict)


class StoreVectorsView(APIView):
    async def post(self, request: Request) -> Response:
        serializer = VectorStoreRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        vector_db = await VectorDBService.get_instance()

        ids = await vector_db.store_vectors(data["resume_id"], data["vectors"])
        return Response({"status": "success", "vector_count": len(ids)}, status=status.HTTP_200_OK)


class DeleteResumeView(APIView):
    async def delete(self, request: Request, resume_id: str) -> Response:
        graph_db = await GraphDBService.get_instance()
        vector_db = await VectorDBService.get_instance()

        await graph_db.delete_resume(resume_id=resume_id)
        await vector_db.delete_resume_vectors(resume_id)

        return Response({"status": "success", "message": f"Resume {resume_id} deleted successfully"})
