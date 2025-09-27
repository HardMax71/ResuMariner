import logging
from dataclasses import asdict

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    FilterOptionsSerializer,
    GraphSearchQuerySerializer,
    HybridSearchQuerySerializer,
    SearchResponseSerializer,
    VectorSearchQuerySerializer,
)
from .services.graph_search import GraphSearchService
from .services.search_coordinator import SearchCoordinator

logger = logging.getLogger(__name__)


class SemanticSearchView(APIView):
    def __init__(self):
        super().__init__()
        self.coordinator = SearchCoordinator()

    def post(self, request: Request) -> Response:
        query_serializer = VectorSearchQuerySerializer(data=request.data)
        if not query_serializer.is_valid():
            return Response(query_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        search_request = query_serializer.validated_data
        logger.info("Performing semantic search for query: %s", search_request.query)

        try:
            search_response = self.coordinator.search(search_request)
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return Response({"error": "Search failed"}, status=status.HTTP_400_BAD_REQUEST)

        response_data = asdict(search_response)
        response_serializer = SearchResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)

        return Response(response_serializer.data)


class StructuredSearchView(APIView):
    def __init__(self):
        super().__init__()
        self.coordinator = SearchCoordinator()

    def post(self, request: Request) -> Response:
        query_serializer = GraphSearchQuerySerializer(data=request.data)
        if not query_serializer.is_valid():
            return Response(query_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        search_request = query_serializer.validated_data

        try:
            search_response = self.coordinator.search(search_request)
        except Exception as e:
            logger.error(f"Structured search failed: {e}")
            return Response({"error": "Search failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response_data = asdict(search_response)
        response_serializer = SearchResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)

        return Response(response_serializer.data)


class HybridSearchView(APIView):
    def __init__(self):
        super().__init__()
        self.coordinator = SearchCoordinator()

    def post(self, request: Request) -> Response:
        query_serializer = HybridSearchQuerySerializer(data=request.data)
        if not query_serializer.is_valid():
            return Response(query_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        search_request = query_serializer.validated_data

        try:
            search_response = self.coordinator.search(search_request)
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return Response({"error": "Search failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response_data = asdict(search_response)
        response_serializer = SearchResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)

        return Response(response_serializer.data)


class FilterOptionsView(APIView):
    def get(self, request: Request) -> Response:
        graph_search = GraphSearchService()
        filter_options = graph_search.get_filter_options()
        options_data = asdict(filter_options)

        serializer = FilterOptionsSerializer(data=options_data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data)
