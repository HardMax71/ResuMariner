import logging

logger = logging.getLogger(__name__)

import time

from fastapi import HTTPException, APIRouter

from models.search_models import (
    VectorSearchQuery, GraphSearchQuery, HybridSearchQuery,
    SearchResponse, FilterOptions
)
from services.embedding_service import EmbeddingService
from services.graph_search import GraphSearchService
from services.hybrid_search import HybridSearchService
from services.vector_search import VectorSearchService
from utils.errors import SearchServiceError, EmbeddingError, DatabaseError
from utils.helpers import timed_execution

router = APIRouter()

try:
    embedding_service = EmbeddingService()
    vector_search = VectorSearchService()
    graph_search = GraphSearchService()
    hybrid_search = HybridSearchService()
    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Service initialization error: {str(e)}")
    raise


@router.post("/search/semantic", response_model=SearchResponse)
@timed_execution
async def semantic_search(query: VectorSearchQuery):
    """Search for CVs using semantic similarity

    This endpoint performs a semantic search based on the meaning of the query text.
    The search is powered by vector embeddings and returns results ranked by similarity.

    Examples:
    - "experienced backend developer with Python"
    - "project manager with healthcare industry knowledge"
    - "data scientist with machine learning expertise"
    """
    try:
        start_time = time.time()
        logger.info(f"Performing semantic search for query: {query.query}")

        # Generate embedding for the search query
        query_vector = embedding_service.encode(query.query)

        # Perform vector search
        search_results = vector_search.search(
            query_vector=query_vector,
            limit=query.limit,
            min_score=query.min_score,
            filters=query.filters
        )

        logger.debug(f"Vector search returned {len(search_results)} raw results")

        # Process and format results by grouping them by CV ID
        cv_results = {}

        # Group by CV ID and format according to model
        for hit in search_results:
            cv_id = hit["cv_id"]

            # Initialize the CV entry if it doesn't exist
            if cv_id not in cv_results:
                cv_results[cv_id] = {
                    "cv_id": cv_id,
                    "person_name": hit["person_name"],
                    "email": hit["email"],
                    "matches": [],
                    "score": 0.0,
                    "summary": None,  # These fields may be populated later if available
                    "skills": None,
                    "experiences": None
                }

            # Add this match to the CV's matches list
            cv_results[cv_id]["matches"].append({
                "text": hit["text"],
                "score": hit["score"],
                "source": hit["source"],
                "context": hit["context"]
            })

            # Update the overall score (use max score of all matches)
            cv_results[cv_id]["score"] = max(cv_results[cv_id]["score"], hit["score"])

        # Convert the dictionary to a list and sort by score
        formatted_results = list(cv_results.values())
        formatted_results.sort(key=lambda x: x["score"], reverse=True)

        # Limit results to requested number
        formatted_results = formatted_results[:query.limit]

        logger.info(f"Returning {len(formatted_results)} grouped results")

        execution_time = time.time() - start_time

        return SearchResponse(
            results=formatted_results,
            total=len(formatted_results),
            query=query.query,
            search_type="semantic",
            execution_time=execution_time
        )

    except EmbeddingError as e:
        logger.error(f"Embedding error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Embedding error: {str(e)}")
    except DatabaseError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in semantic search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/search/structured", response_model=SearchResponse)
@timed_execution
async def structured_search(query: GraphSearchQuery):
    """Search for CVs using structured criteria

    This endpoint performs a structured search based on specific criteria like skills,
    technologies, role, etc. Results are returned based on exact matches.

    Examples:
    - Search for candidates with specific skills: ["Python", "Docker", "AWS"]
    - Search for candidates who worked at a specific company: "Google"
    - Search for candidates with a specific role: "Senior Software Engineer"
    """
    try:
        start_time = time.time()

        # Perform graph search
        results = graph_search.search(
            skills=query.skills,
            technologies=query.technologies,
            role=query.role,
            company=query.company,
            location=query.location,
            years_experience=query.years_experience,
            limit=query.limit
        )

        execution_time = time.time() - start_time

        return SearchResponse(
            results=results,
            total=len(results),
            query="Structured search",
            search_type="structured",
            execution_time=execution_time
        )

    except DatabaseError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/search/hybrid", response_model=SearchResponse)
@timed_execution
async def hybrid_search_endpoint(query: HybridSearchQuery):
    """Search for CVs using hybrid approach

    This endpoint combines semantic and structured search for better results.
    It uses both vector similarity and graph-based filtering to find the most relevant candidates.

    Examples:
    - "experienced backend developer with Python" + skills=["AWS", "Docker"]
    - "project manager" + company="Microsoft"
    """
    try:
        # Perform hybrid search
        result = hybrid_search.search(
            query=query.query,
            skills=query.skills,
            technologies=query.technologies,
            role=query.role,
            company=query.company,
            location=query.location,
            vector_weight=query.vector_weight,
            graph_weight=query.graph_weight,
            limit=query.limit
        )

        return SearchResponse(
            results=result["results"],
            total=result["total"],
            query=query.query,
            search_type="hybrid",
            execution_time=result["execution_time"]
        )

    except SearchServiceError as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/filters", response_model=FilterOptions)
async def get_filter_options():
    """Get available filter options for search

    This endpoint provides available options for structured search filters,
    including skills, technologies, roles, companies, and locations.
    Each option includes a count of CVs that have that value.
    """
    try:
        # Get filter options from graph database
        filter_data = graph_search.get_filter_options()

        return FilterOptions(
            skills=filter_data["skills"],
            technologies=filter_data["technologies"],
            roles=filter_data["roles"],
            companies=filter_data["companies"],
            locations=filter_data["locations"]
        )

    except DatabaseError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get filter options: {str(e)}")
