import logging
from dataclasses import dataclass, field
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
            filters=filters,
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
        """Combine and score results from both search methods."""

        @dataclass
        class Agg:
            """Internal aggregation helper."""

            resume_id: str
            name: str = "Unknown"
            email: str = ""
            matches: list[dict[str, Any]] = field(default_factory=list)
            summary: Any | None = None
            skills: list[str] = field(default_factory=list)
            experiences: list[dict[str, Any]] = field(default_factory=list)
            education: list[dict[str, Any]] = field(default_factory=list)
            vector_max: float = 0.0
            graph_sum: float = 0.0
            has_vector: bool = False
            has_graph: bool = False

        by_cv: dict[str, Agg] = {}

        # Process vector results (VectorHit objects)
        for vr in vector_results:
            resume_id = vr.resume_id
            if not resume_id:
                continue

            agg = by_cv.get(resume_id)
            if agg is None:
                agg = Agg(resume_id=resume_id, name=vr.name or "Unknown", email=vr.email or "")
                by_cv[resume_id] = agg

            # Add match from vector result
            agg.matches.append({"text": vr.text, "score": vr.score, "source": vr.source, "context": vr.context or ""})
            agg.vector_max = max(agg.vector_max, vr.score)
            agg.has_vector = True

        # Process graph results (ResumeSearchResult objects)
        for gr in graph_results:
            resume_id = gr.resume_id
            if not resume_id:
                continue

            agg = by_cv.get(resume_id)
            if agg is None:
                agg = Agg(resume_id=resume_id, name=gr.name, email=gr.email)
                by_cv[resume_id] = agg

            # Update with graph result data
            if gr.summary:
                agg.summary = gr.summary
            if gr.skills:
                agg.skills = gr.skills
            if gr.experiences:
                agg.experiences = gr.experiences
            if gr.education:
                agg.education = gr.education

            # Process matches if any - gr.matches are VectorHit objects
            for m in gr.matches:
                agg.matches.append({"text": m.text, "score": m.score, "source": m.source, "context": m.context or ""})

            agg.graph_sum += gr.score
            agg.has_graph = True

        # Score and categorize results
        both: list[tuple[float, Agg]] = []
        only_vector: list[tuple[float, Agg]] = []
        only_graph: list[tuple[float, Agg]] = []

        for agg in by_cv.values():
            # Calculate combined score
            final_score = vector_weight * agg.vector_max + graph_weight * agg.graph_sum
            final_score = min(final_score, 1.0)

            # Sort matches by score and limit them
            if agg.matches:
                agg.matches.sort(key=lambda m: m["score"], reverse=True)
                agg.matches = agg.matches[:max_matches_per_result]

            # Categorize by source
            if agg.has_vector and agg.has_graph:
                both.append((final_score, agg))
            elif agg.has_vector:
                only_vector.append((final_score, agg))
            else:
                only_graph.append((final_score, agg))

        def emit(bucket: list[tuple[float, Agg]], remaining: int) -> list[ResumeSearchResult]:
            """Convert aggregations to result dictionaries."""
            out: list[ResumeSearchResult] = []
            for score, agg in sorted(bucket, key=lambda t: t[0], reverse=True):
                # Convert matches to VectorHit objects
                vector_hits = []
                for m in agg.matches:
                    vector_hits.append(
                        VectorHit(
                            resume_id=agg.resume_id,
                            text=m["text"],
                            score=m["score"],
                            source=m["source"],
                            context=m.get("context"),
                            name=agg.name,
                            email=agg.email,
                        )
                    )

                out.append(
                    ResumeSearchResult(
                        resume_id=agg.resume_id,
                        name=agg.name,
                        email=agg.email,
                        score=score,
                        matches=vector_hits,
                        summary=agg.summary,
                        skills=agg.skills or None,
                        experiences=agg.experiences or None,
                        education=agg.education or None,
                        years_experience=None,
                        location=None,
                        desired_role=None,
                    )
                )
                if len(out) >= remaining:
                    break
            return out

        # Emit results prioritizing those found by both methods
        final_results: list[ResumeSearchResult] = []
        for bucket in (both, only_vector, only_graph):
            if len(final_results) >= limit:
                break
            remaining = limit - len(final_results)
            final_results.extend(emit(bucket, remaining))

        logger.info("Combined search returned %s results", len(final_results))
        return final_results
