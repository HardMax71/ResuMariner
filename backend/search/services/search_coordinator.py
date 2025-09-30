import logging
from collections import defaultdict

from django.conf import settings

from core.domain import (
    ResumeSearchResult,
    SearchRequest,
    SearchResponse,
    SearchType,
    VectorHit,
)
from core.services import EmbeddingService

from .graph_search import GraphSearchService
from .hybrid_search import HybridSearchService
from .vector_search import VectorSearchService

logger = logging.getLogger(__name__)


class SearchCoordinator:
    def __init__(self):
        self.vector_search = VectorSearchService()
        self.graph_search = GraphSearchService()
        self.hybrid_search = HybridSearchService()
        self.embedding_service = EmbeddingService(settings.EMBEDDING_MODEL)

    async def search(self, request: SearchRequest) -> SearchResponse:
        """Main entry point for all search types"""
        if request.search_type == SearchType.SEMANTIC:
            results = await self._semantic_search(request)
        elif request.search_type == SearchType.STRUCTURED:
            results = await self._structured_search(request)
        elif request.search_type == SearchType.HYBRID:
            results = await self._hybrid_search(request)
        else:
            raise ValueError(f"Unknown search type: {request.search_type}")

        return SearchResponse(
            results=results, query=request.query or "", search_type=request.search_type, total_found=len(results)
        )

    async def _semantic_search(self, request: SearchRequest) -> list[ResumeSearchResult]:
        if not request.query:
            raise ValueError("Query is required for semantic search")

        query_vector = self.embedding_service.encode(request.query)

        vector_hits = await self.vector_search.search(
            query_vector=query_vector,
            limit=request.limit * 5,  # Over-fetch for grouping
            min_score=request.min_score,
            filters=None,
        )

        grouped = self._group_vector_hits_by_resume_id(vector_hits)

        resume_ids = list(grouped.keys())
        complete_resumes = await self.graph_search.get_resumes_by_ids(resume_ids)

        # Create a map for quick lookup
        resume_map = {r.resume_id: r for r in complete_resumes}

        # Combine vector hits with complete resume data
        results = []
        for resume_id, hits in grouped.items():
            if resume_id in resume_map:
                # Use complete data from graph
                result = resume_map[resume_id]
                # Keep the VectorHit objects for matches, just limit them
                result.matches = hits[: request.max_matches_per_result]
                result.score = max(hit.score for hit in hits)
            else:
                # Fallback if not found in graph (shouldn't happen normally)
                limited_hits = hits[: request.max_matches_per_result]
                result = ResumeSearchResult.from_matches(resume_id, limited_hits)

            results.append(result)

        # Sort by score and limit
        results.sort(key=lambda r: r.score, reverse=True)
        return results[: request.limit]

    async def _structured_search(self, request: SearchRequest) -> list[ResumeSearchResult]:
        return await self.graph_search.search(filters=request.filters, limit=request.limit)

    async def _hybrid_search(self, request: SearchRequest) -> list[ResumeSearchResult]:
        return await self.hybrid_search.search(
            query=request.query or "",
            filters=request.filters,
            vector_weight=request.vector_weight,
            graph_weight=request.graph_weight,
            limit=request.limit,
            max_matches_per_result=request.max_matches_per_result,
        )

    def _group_vector_hits_by_resume_id(self, hits: list[VectorHit]) -> dict[str, list[VectorHit]]:
        grouped = defaultdict(list)
        for hit in hits:
            grouped[hit.resume_id].append(hit)
        return dict(grouped)
