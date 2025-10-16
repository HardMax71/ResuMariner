import logging
from collections import defaultdict

from core.domain import ResumeSearchResult, VectorHit

logger = logging.getLogger(__name__)


async def enrich_vector_hits_with_resume_data(
    vector_hits: list[VectorHit],
    graph_search,  # GraphSearchService (avoid import for circular dependency)
    max_matches_per_result: int,
    limit: int,
) -> list[ResumeSearchResult]:
    """
    Transform vector hits into complete ResumeSearchResult objects.

    Args:
        vector_hits: Matching text chunks from Qdrant vector search
        graph_search: GraphSearchService instance for fetching complete resume data
        max_matches_per_result: Max vector matches to include per resume
        limit: Max results to return

    Returns:
        Sorted, limited list of complete resume search results with attached matches
    """
    if not vector_hits:
        return []

    # Group hits by resume UID
    grouped = defaultdict(list)
    for hit in vector_hits:
        grouped[hit.uid].append(hit)

    # Fetch complete resume data from Neo4j
    uids = list(grouped.keys())
    complete_resumes = await graph_search.get_resumes_by_ids(uids)
    resume_map = {r.uid: r for r in complete_resumes}

    # Merge vector matches with resume data
    results = []
    for uid, hits in grouped.items():
        if uid in resume_map:
            # Resume found - attach matches
            result = resume_map[uid]
            result.matches = hits[:max_matches_per_result]
            result.score = max(hit.score for hit in hits)
        else:
            # Data corruption: resume in Qdrant but missing from Neo4j
            logger.warning("Resume %s found in Qdrant but missing in Neo4j", uid)
            result = ResumeSearchResult.from_matches(uid, hits[:max_matches_per_result])

        results.append(result)

    # Sort by relevance and limit
    results.sort(key=lambda r: r.score, reverse=True)
    return results[:limit]
