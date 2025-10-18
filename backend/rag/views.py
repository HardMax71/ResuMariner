import logging

from adrf.views import APIView
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import (
    CompareCandidatesRequestSerializer,
    ExplainMatchRequestSerializer,
    InterviewQuestionsRequestSerializer,
)

logger = logging.getLogger(__name__)


class ExplainMatchView(APIView):
    throttle_scope = "rag"

    @extend_schema(
        request=ExplainMatchRequestSerializer,
        responses={
            200: OpenApiResponse(description="Structured match explanation"),
            404: OpenApiResponse(description="Resume not found"),
        },
        description="Generate AI-powered explanation of candidate-job fit with structured strengths, concerns, and recommendations.",
    )
    async def post(self, request: Request) -> Response:
        serializer = ExplainMatchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        resume_uid = serializer.validated_data["resume_uid"]
        job_description = serializer.validated_data["job_description"]

        explanation = await request.rag_service.explain_match(resume_uid, job_description)

        return Response(explanation.model_dump(), status=status.HTTP_200_OK)


class CompareCandidatesView(APIView):
    throttle_scope = "rag"

    @extend_schema(
        request=CompareCandidatesRequestSerializer,
        responses={
            200: OpenApiResponse(description="Structured candidate comparison"),
            400: OpenApiResponse(description="Invalid request"),
            404: OpenApiResponse(description="One or more resumes not found"),
        },
        description="Compare 2-5 candidates across multiple dimensions with scenario-based recommendations.",
    )
    async def post(self, request: Request) -> Response:
        serializer = CompareCandidatesRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comparison = await request.rag_service.compare_candidates(
            candidate_uids=serializer.validated_data["resume_uids"],
            criteria=serializer.validated_data.get("criteria"),
            job_context=serializer.validated_data.get("job_context"),
        )

        return Response(comparison.model_dump(), status=status.HTTP_200_OK)


class InterviewQuestionsView(APIView):
    throttle_scope = "rag"

    @extend_schema(
        request=InterviewQuestionsRequestSerializer,
        responses={
            200: OpenApiResponse(description="Structured interview question set"),
            404: OpenApiResponse(description="Resume not found"),
        },
        description="Generate 6-12 interview questions tailored to candidate's background, with follow-ups and assessment criteria.",
    )
    async def post(self, request: Request) -> Response:
        serializer = InterviewQuestionsRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question_set = await request.rag_service.generate_interview_questions(
            candidate_uid=serializer.validated_data["resume_uid"],
            interview_type=serializer.validated_data.get("interview_type", "technical"),
            role_context=serializer.validated_data.get("role_context"),
            focus_areas=serializer.validated_data.get("focus_areas"),
        )

        return Response(question_set.model_dump(), status=status.HTTP_200_OK)
