import logging
from dataclasses import asdict

from adrf.views import APIView
from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import (
    FilterOptionsSerializer,
    GraphSearchQuerySchema,
    HybridSearchQuerySchema,
    SearchResponseSerializer,
    VectorSearchQuerySchema,
)

logger = logging.getLogger(__name__)

THROTTLE_RATES: dict[str, str] = settings.REST_FRAMEWORK.get("DEFAULT_THROTTLE_RATES", {})  # type: ignore[assignment]


class SemanticSearchView(APIView):
    """Semantic search endpoint using vector embeddings."""

    throttle_scope = "search"

    @extend_schema(
        request=VectorSearchQuerySchema,
        responses={
            200: SearchResponseSerializer,
            429: OpenApiResponse(description=f"Rate limit exceeded ({THROTTLE_RATES.get('search', 'N/A')})"),
        },
        description="Perform semantic search using vector embeddings. Searches resume content by semantic similarity.",
    )
    async def post(self, request: Request) -> Response:
        serializer = VectorSearchQuerySchema(data=request.data)
        serializer.is_valid(raise_exception=True)

        logger.debug("Performing semantic search for query: %s", serializer.validated_data.query)

        result = await request.search_coordinator.search(serializer.validated_data)
        return Response(asdict(result))


class StructuredSearchView(APIView):
    """Structured search endpoint using graph filters."""

    throttle_scope = "search"

    @extend_schema(
        request=GraphSearchQuerySchema,
        responses={
            200: SearchResponseSerializer,
            429: OpenApiResponse(description=f"Rate limit exceeded ({THROTTLE_RATES.get('search', 'N/A')})"),
        },
        description="Perform structured search using graph filters. Filters resumes by skills, role, company, location, and experience.",
    )
    async def post(self, request: Request) -> Response:
        serializer = GraphSearchQuerySchema(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = await request.search_coordinator.search(serializer.validated_data)
        return Response(asdict(result))


class HybridSearchView(APIView):
    """Hybrid search endpoint combining semantic and structured approaches."""

    throttle_scope = "search"

    @extend_schema(
        request=HybridSearchQuerySchema,
        responses={
            200: SearchResponseSerializer,
            429: OpenApiResponse(description=f"Rate limit exceeded ({THROTTLE_RATES.get('search', 'N/A')})"),
        },
        description="Perform hybrid search combining semantic and structured approaches. Weighted combination of vector and graph search.",
    )
    async def post(self, request: Request) -> Response:
        serializer = HybridSearchQuerySchema(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = await request.search_coordinator.search(serializer.validated_data)
        return Response(asdict(result))


class FilterOptionsView(APIView):
    """Get available filter options for search."""

    @extend_schema(
        responses={200: FilterOptionsSerializer},
        description="Get available filter options for search. Returns lists of skills, roles, companies, and locations with counts.",
    )
    async def get(self, request: Request) -> Response:
        result = await request.search_coordinator.graph_search.get_filter_options()
        return Response(asdict(result))
