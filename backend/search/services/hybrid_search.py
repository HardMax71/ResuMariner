import logging
from collections import defaultdict
from typing import Any

from django.conf import settings

from core.domain import ResumeSearchResult, SearchFilters, VectorHit
from core.services import EmbeddingService

from .graph_search import GraphSearchService
from .vector_search import VectorSearchService

logger = logging.getLogger(__name__)


class HybridSearchService:
    """Service that combines vector and graph search approaches."""

    def __init__(self):
        self.vector_search = VectorSearchService()
        self.graph_search = GraphSearchService()
        self.embedding_service = EmbeddingService()

    async def search(
        self,
        query: str,
        filters: SearchFilters,
        vector_weight: float = settings.DEFAULT_VECTOR_WEIGHT,
        graph_weight: float = settings.DEFAULT_GRAPH_WEIGHT,
        limit: int = 10,
        max_matches_per_result: int = 10,
    ) -> list[ResumeSearchResult]:
        """
        Perform hybrid search combining vector and graph approaches.

        Returns list of ResumeSearchResult objects.
        """
        query_vector = self.embedding_service.encode(query)

        vector_results = await self.vector_search.search(
            query_vector=query_vector,
            limit=limit * 2,
            filters=None,  # Semantic search only - no filters
        )

        graph_results = await self.graph_search.search(
            filters=filters,
            limit=limit * 2,
        )

        return self._combine_results(
            vector_results, graph_results, vector_weight, graph_weight, limit, max_matches_per_result
        )

    def _combine_results(
        self,
        vector_results: list[VectorHit],
        graph_results: list[ResumeSearchResult],
        vector_weight: float,
        graph_weight: float,
        limit: int,
        max_matches_per_result: int,
    ) -> list[ResumeSearchResult]:
        """Combine and score results from both search methods using weighted scoring."""

        # Phase 1: Aggregate data by uid
        aggregated: dict[str, dict[str, Any]] = defaultdict(
            lambda: {
                "matches": [],
                "vector_score": 0.0,
                "graph_score": 0.0,
                "has_vector": False,
                "has_graph": False,
            }
        )

        for vr in vector_results:
            agg = aggregated[vr.uid]
            agg["uid"] = vr.uid
            agg["matches"].append(
                {"text": vr.text, "score": vr.score, "source": vr.source, "context": vr.context or ""}
            )
            agg["vector_score"] = max(agg["vector_score"], vr.score)
            agg["has_vector"] = True

        # Collect graph data and scores
        for gr in graph_results:
            agg = aggregated[gr.uid]
            agg.update(
                {
                    "uid": gr.uid,
                    "name": gr.name,
                    "email": gr.email,
                    "summary": gr.summary,
                    "skills": gr.skills,
                    "experiences": gr.experiences,
                    "education": gr.education,
                    "years_experience": gr.years_experience,
                    "location": gr.location,
                    "desired_role": gr.desired_role,
                    "languages": gr.languages,
                }
            )
            agg["graph_score"] += gr.score
            agg["has_graph"] = True

        scored = []
        for agg in aggregated.values():
            if not agg["has_graph"]:
                logger.warning("Resume %s found in vector search but missing in Neo4j", agg["uid"])
                agg["name"] = "[Missing Data]"
                agg["email"] = ""

            final_score = min(vector_weight * agg["vector_score"] + graph_weight * agg["graph_score"], 1.0)
            matches = sorted(agg["matches"], key=lambda m: m["score"], reverse=True)[:max_matches_per_result]
            priority = 0 if (agg["has_vector"] and agg["has_graph"]) else (1 if agg["has_vector"] else 2)
            scored.append((priority, -final_score, agg["uid"], agg, matches))  # Add uid as tiebreaker

        # Sort by priority first, then by score, then by uid (for stable sort)
        scored.sort(key=lambda x: (x[0], x[1], x[2]))

        # Phase 3: Convert to ResumeSearchResult objects
        results = []
        for _priority, neg_score, _uid, agg, matches in scored[:limit]:
            vector_hits = [
                VectorHit(
                    uid=agg["uid"],
                    text=m["text"],
                    score=m["score"],
                    source=m["source"],
                    context=m.get("context"),
                )
                for m in matches
            ]

            results.append(
                ResumeSearchResult(
                    uid=agg["uid"],
                    name=agg["name"],
                    email=agg["email"],
                    score=-neg_score,
                    matches=vector_hits,
                    summary=agg.get("summary"),
                    skills=agg.get("skills"),
                    experiences=agg.get("experiences"),
                    education=agg.get("education"),
                    years_experience=agg.get("years_experience"),
                    location=agg.get("location"),
                    desired_role=agg.get("desired_role"),
                    languages=agg.get("languages"),
                )
            )

        logger.info("Combined search returned %s results", len(results))
        return results
