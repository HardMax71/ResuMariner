import asyncio
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


def timed_execution(func):
    """Decorator to measure execution time of a function
    Works with both synchronous and asynchronous functions"""

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        execution_time = time.time() - start_time

        # If result is a dict, add execution_time
        if isinstance(result, dict) and "execution_time" not in result:
            result["execution_time"] = execution_time

        logger.debug(
            f"Function {func.__name__} executed in {execution_time:.4f} seconds"
        )
        return result

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time

        # If result is a dict, add execution_time
        if isinstance(result, dict) and "execution_time" not in result:
            result["execution_time"] = execution_time

        logger.debug(
            f"Function {func.__name__} executed in {execution_time:.4f} seconds"
        )
        return result

    # Choose the appropriate wrapper based on whether the function is async
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def combine_search_results(
    vector_results, graph_results, vector_weight, graph_weight, limit
):
    """Combine and rank results from different search methods

    Args:
        vector_results: Results from vector search
        graph_results: Results from graph search
        vector_weight: Weight for vector scores (0-1)
        graph_weight: Weight for graph scores (0-1)
        limit: Maximum number of results to return

    Returns:
        Combined and ranked results
    """
    # Normalize weights to ensure they sum to 1
    total_weight = vector_weight + graph_weight
    if total_weight == 0:
        # Default to equal weights if both are 0
        vector_weight = graph_weight = 0.5
    else:
        vector_weight = vector_weight / total_weight
        graph_weight = graph_weight / total_weight

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
                "score": 0,
            }

        # Add match to the CV's matches list
        cv_details[cv_id]["matches"].append(
            {
                "text": result["text"],
                "score": result["score"],
                "source": result["source"],
                "context": result["context"],
            }
        )

        # Update the combined score - for vector results, use the maximum match score
        match_score = result["score"] * vector_weight
        if combined_scores[cv_id] < match_score:
            combined_scores[cv_id] = match_score

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
                "score": 0,
            }

        # Add additional details from graph search
        if result.get("summary"):
            cv_details[cv_id]["summary"] = result["summary"]

        if result.get("skills"):
            cv_details[cv_id]["skills"] = result["skills"]

        if result.get("experiences"):
            cv_details[cv_id]["experiences"] = result["experiences"]

        # For graph results, add the weighted score to the combined score
        combined_scores[cv_id] += result["score"] * graph_weight

    # Prioritize CVs found in both searches
    both_searches = vector_cvs.intersection(graph_cvs)
    only_vector = vector_cvs - both_searches
    only_graph = graph_cvs - both_searches

    # Final results list
    sorted_results = []

    # First add CVs from both searches, sorted by score
    for cv_set in [both_searches, only_vector, only_graph]:
        # Sort CVs in this set by score
        sorted_cvs = sorted(
            [(cv_id, combined_scores[cv_id]) for cv_id in cv_set],
            key=lambda x: x[1],
            reverse=True,
        )

        # Add to final results
        for cv_id, score in sorted_cvs:
            result = cv_details[cv_id]
            result["score"] = score
            sorted_results.append(result)

            # Stop if we've reached the limit
            if len(sorted_results) >= limit:
                break

        if len(sorted_results) >= limit:
            break

    return sorted_results[:limit]
