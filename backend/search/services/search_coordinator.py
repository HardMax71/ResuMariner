import logging
from typing import assert_never

from rest_framework.exceptions import ValidationError

from core.domain import ResumeSearchResult, SearchRequest, SearchResponse, SearchType
from core.services import EmbeddingService

from .graph_search import GraphSearchService
from .hybrid_search import HybridSearchService
from .result_enrichment import enrich_vector_hits_with_resume_data
from .vector_search import VectorSearchService

logger = logging.getLogger(__name__)


class SearchCoordinator:
    """Coordinates all search types and delegates to specialized services."""

    def __init__(self):
        self.vector_search = VectorSearchService()
        self.graph_search = GraphSearchService()
        self.embedding_service = EmbeddingService()
        self.hybrid_search = HybridSearchService(
            vector_search=self.vector_search,
            graph_search=self.graph_search,
            embedding_service=self.embedding_service,
        )

    async def search(self, request: SearchRequest) -> SearchResponse:
        """Main entry point for all search types"""
        if request.search_type == SearchType.SEMANTIC:
            results = await self._semantic_search(request)
        elif request.search_type == SearchType.STRUCTURED:
            results = await self._structured_search(request)
        elif request.search_type == SearchType.HYBRID:
            results = await self._hybrid_search(request)
        else:
            assert_never(request.search_type)

        return SearchResponse(
            results=results, query=request.query or "", search_type=request.search_type, total_found=len(results)
        )

    async def _semantic_search(self, request: SearchRequest) -> list[ResumeSearchResult]:
        if not request.query:
            logger.error("Semantic search attempted without query")
            raise ValidationError("Query is required for semantic search")

        query_vector = await self.embedding_service.encode(request.query)

        vector_hits = await self.vector_search.search(
            query_vector=query_vector,
            limit=request.limit * 5,  # Over-fetch for grouping
            min_score=request.min_score,
        )

        return await enrich_vector_hits_with_resume_data(
            vector_hits,
            self.graph_search,
            request.max_matches_per_result,
            request.limit,
        )

    async def _structured_search(self, request: SearchRequest) -> list[ResumeSearchResult]:
        return await self.graph_search.search(filters=request.filters, limit=request.limit)

    async def _hybrid_search(self, request: SearchRequest) -> list[ResumeSearchResult]:
        return await self.hybrid_search.search(
            query=request.query or "",
            filters=request.filters,
            limit=request.limit,
            max_matches_per_result=request.max_matches_per_result,
        )

    async def close(self) -> None:
        """Cleanup all service connections."""
        await self.vector_search.close()
        await self.graph_search.close()
        logger.info("SearchCoordinator connections closed")
