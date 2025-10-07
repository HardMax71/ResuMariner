import logging
import uuid

from django.conf import settings
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qdrant_models

from core.domain import EmbeddingVector

logger = logging.getLogger(__name__)


class VectorDBService:
    _configured: bool = False
    _client: AsyncQdrantClient | None = None
    _instance: "VectorDBService | None" = None

    def __init__(self, client: AsyncQdrantClient) -> None:
        self.client = client
        self.collection_name = settings.QDRANT_COLLECTION
        self.vector_size = settings.VECTOR_SIZE

    @classmethod
    async def configure(cls) -> None:
        if cls._configured:
            return

        client = AsyncQdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            timeout=settings.QDRANT_TIMEOUT,
            prefer_grpc=settings.QDRANT_PREFER_GRPC,
        )

        await cls._ensure_collection(client)

        cls._client = client
        cls._configured = True
        logger.info("VectorDBService configured with Qdrant at %s:%s", settings.QDRANT_HOST, settings.QDRANT_PORT)

    @classmethod
    async def get_instance(cls) -> "VectorDBService":
        if not cls._configured or cls._client is None:
            await cls.configure()

        assert cls._client is not None
        if cls._instance is None:
            cls._instance = cls(cls._client)

        return cls._instance

    @classmethod
    async def _ensure_collection(cls, client: AsyncQdrantClient) -> None:
        collections = await client.get_collections()
        names = [c.name for c in collections.collections]
        collection_name = settings.QDRANT_COLLECTION
        vector_size = settings.VECTOR_SIZE

        if collection_name in names:
            return

        logger.info("Creating Qdrant collection %s with vector size %s", collection_name, vector_size)

        await client.create_collection(
            collection_name=collection_name,
            vectors_config=qdrant_models.VectorParams(
                size=vector_size,
                distance=qdrant_models.Distance.COSINE,
            ),
        )

        keyword_fields = ["resume_id", "name", "source", "email", "skills", "companies", "role", "location"]
        for field in keyword_fields:
            await client.create_payload_index(
                collection_name=collection_name,
                field_name=field,
                field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
            )

        await client.create_payload_index(
            collection_name=collection_name,
            field_name="years_experience",
            field_schema=qdrant_models.PayloadSchemaType.INTEGER,
        )

    async def delete_resume_vectors(self, resume_id: str) -> int:
        f = qdrant_models.Filter(
            must=[qdrant_models.FieldCondition(key="resume_id", match=qdrant_models.MatchValue(value=resume_id))]
        )

        count_result = await self.client.count(
            collection_name=self.collection_name,
            count_filter=f,
        )
        count = int(getattr(count_result, "count", 0))
        if count > 0:
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=qdrant_models.FilterSelector(filter=f),
                wait=True,
            )
        return count

    async def store_vectors(self, resume_id: str, vectors: list[EmbeddingVector]) -> list[str]:
        if not vectors:
            logger.warning("No vectors to store for resume %s", resume_id)
            return []

        await self.delete_resume_vectors(resume_id)

        points: list[qdrant_models.PointStruct] = []
        for idx, v in enumerate(vectors):
            vec = v.vector
            if len(vec) != self.vector_size:
                logger.warning(
                    "Vector dimension mismatch at index %s for resume %s: got %s",
                    idx,
                    resume_id,
                    len(vec) if isinstance(vec, list) else None,
                )
                continue
            pid = str(uuid.uuid4())
            payload = {
                "resume_id": resume_id,
                "text": v.text,
                "source": v.source,
                "context": v.context,
                "name": v.name,
                "email": v.email,
                "skills": v.skills,
                "companies": v.companies,
                "role": v.role,
                "location": v.location,
                "years_experience": v.years_experience,
            }
            points.append(qdrant_models.PointStruct(id=pid, vector=vec, payload=payload))

        if not points:
            return []

        await self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )
        return [str(p.id) for p in points]
