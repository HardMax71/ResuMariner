import logging
from dataclasses import asdict

from django.conf import settings
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qdrant_models

from core.domain import SearchFilters, VectorHit

logger = logging.getLogger(__name__)


class VectorSearchService:
    def __init__(self):
        self.client = AsyncQdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        self.collection_name = settings.QDRANT_COLLECTION
        logger.info("Connected to Qdrant at %s:%s", settings.QDRANT_HOST, settings.QDRANT_PORT)

    async def search(
        self,
        query_vector: list[float],
        limit: int = 10,
        min_score: float = 0.0,
        filters: SearchFilters | None = None,
    ) -> list[VectorHit]:
        # Convert SearchFilters to Qdrant filter conditions
        filter_dict = asdict(filters) if filters else {}
        conditions: list[qdrant_models.FieldCondition] = [
            qdrant_models.FieldCondition(
                key=key,
                match=(
                    qdrant_models.MatchAny(any=value)
                    if isinstance(value, list)
                    else qdrant_models.MatchValue(value=value)
                ),
            )
            for key, value in filter_dict.items()
            if value is not None
        ]
        query_filter = qdrant_models.Filter(must=conditions) if conditions else None  # type: ignore

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
                continue

            uid = point.payload.get("uid")
            if not uid:
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

    async def close(self):
        """Close the client connection"""
        await self.client.close()
