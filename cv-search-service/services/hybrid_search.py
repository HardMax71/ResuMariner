import logging
import time
from typing import List, Dict, Any, Optional

from config import settings
from services.embedding_service import EmbeddingService
from services.graph_search import GraphSearchService
from services.vector_search import VectorSearchService
from utils.errors import SearchServiceError

logger = logging.getLogger(__name__)


class HybridSearchService:
    """Service for hybrid search combining vector and graph approaches"""

    def __init__(self):
        """Initialize hybrid search service"""
        self.vector_search = VectorSearchService()
        self.graph_search = GraphSearchService()
        self.embedding_service = EmbeddingService()

    def search(self,
               query: str,
               skills: Optional[List[str]] = None,
               technologies: Optional[List[str]] = None,
               role: Optional[str] = None,
               company: Optional[str] = None,
               location: Optional[str] = None,
               vector_weight: float | None = None,
               graph_weight: float | None = None,
               limit: int = 10) -> Dict[str, Any]:
        """Perform hybrid search combining vector and graph approaches"""
        start_time = time.time()

        # Set default weights if not provided
        if vector_weight is None:
            vector_weight = settings.DEFAULT_VECTOR_WEIGHT
        if graph_weight is None:
            graph_weight = settings.DEFAULT_GRAPH_WEIGHT

        try:
            # Generate embedding for the query
            query_vector = self.embedding_service.encode(query)

            # Determine if we need filters for vector search
            vector_filters: Dict[str, Any] = {}
            if skills:
                vector_filters["skills"] = skills
            if company:
                vector_filters["company"] = company

            # Perform vector search
            vector_results = self.vector_search.search(
                query_vector=query_vector,
                limit=limit * 2,  # Get more results to allow for filtering
                filters=vector_filters if vector_filters else None
            )
            logger.debug(f"Vector search returned {len(vector_results)} results")

            # Perform graph search with structured filters
            graph_results = self.graph_search.search(
                skills=skills,
                technologies=technologies,
                role=role,
                company=company,
                location=location,
                limit=limit * 2  # Get more results to allow for merging
            )
            logger.debug(f"Graph search returned {len(graph_results)} results")

            # Combine and rank results
            combined_results = self._combine_results(
                vector_results,
                graph_results,
                vector_weight,
                graph_weight,
                limit
            )

            # Calculate execution time
            execution_time = time.time() - start_time

            return {
                "results": combined_results,
                "total": len(combined_results),
                "execution_time": execution_time,
                "search_type": "hybrid",
                "query": query
            }

        except Exception as e:
            logger.error(f"Hybrid search error: {str(e)}")
            raise SearchServiceError(f"Hybrid search failed: {str(e)}")

    def _combine_results(self,
                         vector_results: List[Dict[str, Any]],
                         graph_results: List[Dict[str, Any]],
                         vector_weight: float,
                         graph_weight: float,
                         limit: int) -> List[Dict[str, Any]]:
        """Combine and rank results from vector and graph searches"""
        # Create dictionaries to track combined scores and store CV details
        combined_scores = {}
        cv_details = {}

        # Track which search found each CV
        vector_cvs = set()
        graph_cvs = set()

        # Process vector search results
        for result in vector_results:
            cv_id = result["cv_id"]
            vector_cvs.add(cv_id)

            # Initialize if this is the first time seeing this CV
            if cv_id not in combined_scores:
                combined_scores[cv_id] = 0
                cv_details[cv_id] = {
                    "cv_id": cv_id,
                    "person_name": result["person_name"],
                    "email": result["email"],
                    "matches": [],
                    "skills": [],
                    "experiences": [],
                    "summary": None,
                    "score": 0
                }

            # Add match to the CV's matches list
            cv_details[cv_id]["matches"].append({
                "text": result["text"],
                "score": result["score"],
                "source": result["source"],
                "context": result["context"]
            })

            # Update the combined score with vector weight
            # For vector results, we take the maximum of all match scores
            current_score = combined_scores[cv_id]
            weighted_score = result["score"] * vector_weight
            combined_scores[cv_id] = max(current_score, weighted_score)

        # Process graph search results
        for result in graph_results:
            cv_id = result["cv_id"]
            graph_cvs.add(cv_id)

            # Initialize if this is the first time seeing this CV
            if cv_id not in combined_scores:
                combined_scores[cv_id] = 0
                cv_details[cv_id] = {
                    "cv_id": cv_id,
                    "person_name": result["person_name"],
                    "email": result["email"],
                    "matches": [],
                    "skills": [],
                    "experiences": [],
                    "summary": None,
                    "score": 0
                }

            # Update CV details with graph data
            if result.get("summary"):
                cv_details[cv_id]["summary"] = result["summary"]

            if result.get("skills"):
                cv_details[cv_id]["skills"] = result["skills"]

            if result.get("experiences"):
                cv_details[cv_id]["experiences"] = result["experiences"]

            # Include any match data from graph results (if present)
            if result.get("matches"):
                cv_details[cv_id]["matches"].extend(result["matches"])

            # Add graph score to combined score
            combined_scores[cv_id] += result["score"] * graph_weight

        # Prioritize results found in both searches, then vector-only, then graph-only
        both_searches = vector_cvs.intersection(graph_cvs)
        only_vector = vector_cvs - both_searches
        only_graph = graph_cvs - both_searches

        # Prepare final results
        final_results = []

        # Process each group in priority order
        for cv_group in [both_searches, only_vector, only_graph]:
            # Sort this group by score
            sorted_group = sorted([(cv_id, combined_scores[cv_id]) for cv_id in cv_group],
                                  key=lambda x: x[1], reverse=True)

            # Add to final results
            for cv_id, score in sorted_group:
                result = cv_details[cv_id]

                # Normalize score to range 0-1
                result["score"] = min(score, 1.0)

                # Sort matches by score for better display
                if result["matches"]:
                    result["matches"].sort(key=lambda m: m["score"], reverse=True)

                final_results.append(result)

                # Stop if we've reached the limit
                if len(final_results) >= limit:
                    break

            # Stop processing groups if we've reached the limit
            if len(final_results) >= limit:
                break

        logger.info(f"Combined search returned {len(final_results)} results")
        return final_results
