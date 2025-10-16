import logging

from core.domain import ResumeSearchResult, SearchFilters
from core.services import EmbeddingService

from .graph_search import GraphSearchService
from .result_enrichment import enrich_vector_hits_with_resume_data
from .vector_search import VectorSearchService

logger = logging.getLogger(__name__)


class HybridSearchService:
    """
    Service that performs hybrid search: semantic relevance within structurally filtered candidates.

    Flow:
    1. Graph search with filters → candidate UIDs
    2. Vector search within those candidates → semantically ranked results
    3. Enrich with complete resume data from Neo4j
    """

    def __init__(
        self,
        vector_search: VectorSearchService,
        graph_search: GraphSearchService,
        embedding_service: EmbeddingService,
    ):
        self.vector_search = vector_search
        self.graph_search = graph_search
        self.embedding_service = embedding_service

    async def search(
        self,
        query: str,
        filters: SearchFilters,
        limit: int = 10,
        max_matches_per_result: int = 10,
    ) -> list[ResumeSearchResult]:
        """
        Perform hybrid search: semantic relevance within filtered candidates.

        Args:
            query: Natural language search query
            filters: Structured filters (skills, location, etc.) - these are REQUIREMENTS
            limit: Maximum number of results to return
            max_matches_per_result: Maximum vector matches to include per resume

        Returns:
            List of resumes matching filters, ranked by semantic relevance to query
        """
        # Step 1: Get candidate UIDs from graph search with filters
        graph_results = await self.graph_search.search(
            filters=filters,
            limit=limit * 3,  # Get more candidates for better semantic selection
        )

        if not graph_results:
            logger.debug("No candidates found matching filters")
            return []

        candidate_uids = [r.uid for r in graph_results]
        logger.debug("Found %d candidates matching filters", len(candidate_uids))

        # Step 2: Semantic search within candidates only
        query_vector = await self.embedding_service.encode(query)
        vector_hits = await self.vector_search.search(
            query_vector=query_vector,
            limit=limit * 5,  # Over-fetch for grouping
            candidate_uids=candidate_uids,
        )

        if not vector_hits:
            logger.debug("No semantic matches found within filtered candidates")
            return []

        # Step 3-6: Enrich vector hits with complete resume data
        results = await enrich_vector_hits_with_resume_data(
            vector_hits,
            self.graph_search,
            max_matches_per_result,
            limit,
        )

        logger.debug("Hybrid search returned %d results", len(results))
        return results
