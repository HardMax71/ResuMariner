import logging

from django.conf import settings
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qdrant_models

from core.domain import VectorHit
from core.metrics import QDRANT_CORRUPTED_POINTS

logger = logging.getLogger(__name__)


class VectorSearchService:
    """Qdrant-based semantic search for resume chunks."""

    def __init__(self):
        self.client = AsyncQdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        self.collection_name = settings.QDRANT_COLLECTION
        logger.info("Connected to Qdrant at %s:%s", settings.QDRANT_HOST, settings.QDRANT_PORT)

    async def search(
        self,
        query_vector: list[float],
        limit: int = 10,
        min_score: float = 0.0,
        candidate_uids: list[str] | None = None,
    ) -> list[VectorHit]:
        """
        Search for semantically similar resume chunks.

        Args:
            query_vector: Encoded query embedding
            limit: Maximum number of results
            min_score: Minimum similarity score threshold
            candidate_uids: Optional list of resume UIDs to restrict search to (for hybrid search)
        """
        query_filter = None
        if candidate_uids:
            query_filter = qdrant_models.Filter(
                must=[qdrant_models.FieldCondition(key="uid", match=qdrant_models.MatchAny(any=candidate_uids))]
            )

        response = await self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            query_filter=query_filter,
            score_threshold=min_score,
            with_payload=True,
            with_vectors=False,
        )

        results = []
        for point in response.points:
            if not point.payload:
                logger.error("DATA CORRUPTION: Point %s has no payload, skipping", point.id)
                QDRANT_CORRUPTED_POINTS.labels(corruption_type="missing_payload").inc()
                continue

            uid = point.payload.get("uid")
            if not uid:
                logger.error("DATA CORRUPTION: Point %s missing uid in payload, skipping", point.id)
                QDRANT_CORRUPTED_POINTS.labels(corruption_type="missing_uid").inc()
                continue

            results.append(
                VectorHit(
                    uid=uid,
                    text=point.payload.get("text", ""),
                    score=point.score,
                    source=point.payload.get("source", "unknown"),
                    context=point.payload.get("context"),
                )
            )

        return results

    async def close(self) -> None:
        """Close Qdrant client connection."""
        await self.client.close()
