import logging
import uuid

from django.conf import settings
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qdrant_models

from core.domain import EmbeddingVector

logger = logging.getLogger(__name__)


class VectorDBService:
    def __init__(self, client: AsyncQdrantClient) -> None:
        self.client = client
        self.collection_name = settings.QDRANT_COLLECTION
        self.vector_size = settings.VECTOR_SIZE

    async def delete_resume_vectors(self, uid: str) -> int:
        f = qdrant_models.Filter(
            must=[qdrant_models.FieldCondition(key="uid", match=qdrant_models.MatchValue(value=uid))]
        )

        count_result = await self.client.count(
            collection_name=self.collection_name,
            count_filter=f,
        )
        count = int(count_result.count if count_result.count else 0)
        if count > 0:
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=qdrant_models.FilterSelector(filter=f),
                wait=True,
            )
        return count

    async def store_vectors(self, uid: str, vectors: list[EmbeddingVector]) -> list[str]:
        if not vectors:
            logger.warning("No vectors to store for resume %s", uid)
            return []

        await self.delete_resume_vectors(uid)

        points: list[qdrant_models.PointStruct] = []
        for idx, v in enumerate(vectors):
            vec = v.vector
            if len(vec) != self.vector_size:
                logger.warning(
                    "Vector dimension mismatch at index %s for resume %s: got %s",
                    idx,
                    uid,
                    len(vec) if vec else None,
                )
                continue
            pid = str(uuid.uuid4())
            payload = v.model_dump(exclude={"vector"})
            payload["uid"] = uid
            points.append(qdrant_models.PointStruct(id=pid, vector=vec, payload=payload))

        if not points:
            return []

        await self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )
        return [str(p.id) for p in points]
