import logging
import uuid

from django.conf import settings
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

from core.domain import EmbeddingVector

logger = logging.getLogger(__name__)


class VectorDBService:
    """Service for storing and managing vectors in Qdrant."""

    def __init__(self) -> None:
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            timeout=settings.QDRANT_TIMEOUT,
            prefer_grpc=settings.QDRANT_PREFER_GRPC,
        )
        self.collection_name = settings.QDRANT_COLLECTION
        self.vector_size = settings.VECTOR_SIZE
        self._ensure_collection()
        logger.info(
            "Connected to Qdrant at %s:%s, collection=%s",
            settings.QDRANT_HOST,
            settings.QDRANT_PORT,
            self.collection_name,
        )

    def _ensure_collection(self) -> None:
        collections = self.client.get_collections().collections
        names = [c.name for c in collections]
        if self.collection_name in names:
            return
        logger.info("Creating collection %s with vector size %s", self.collection_name, self.vector_size)
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=qdrant_models.VectorParams(
                size=self.vector_size,
                distance=qdrant_models.Distance.COSINE,
            ),
        )
        # Index fields for filtering
        keyword_fields = [
            "resume_id",
            "name",
            "source",
            "email",
            "skills",
            "technologies",
            "companies",
            "role",
            "location",
        ]
        for field in keyword_fields:
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name=field,
                field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
            )
        # Index years_experience as integer
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="years_experience",
            field_schema=qdrant_models.PayloadSchemaType.INTEGER,
        )

    def delete_resume_vectors(self, resume_id: str) -> int:
        """Delete all vectors for a resume and return count deleted."""
        f = qdrant_models.Filter(
            must=[qdrant_models.FieldCondition(key="resume_id", match=qdrant_models.MatchValue(value=resume_id))]
        )
        # Count existing
        count_result = self.client.count(
            collection_name=self.collection_name,
            count_filter=f,
        )
        count = int(getattr(count_result, "count", 0))
        if count > 0:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=qdrant_models.FilterSelector(filter=f),
                wait=True,
            )
        return count

    def store_vectors(self, resume_id: str, vectors: list[EmbeddingVector]) -> list[str]:
        if not vectors:
            logger.warning("No vectors to store for resume %s", resume_id)
            return []

        self.delete_resume_vectors(resume_id)

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
                # Add searchable metadata
                "skills": v.skills,
                "technologies": v.technologies,
                "companies": v.companies,
                "role": v.role,
                "location": v.location,
                "years_experience": v.years_experience,
            }
            points.append(qdrant_models.PointStruct(id=pid, vector=vec, payload=payload))

        if not points:
            return []

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )
        return [str(p.id) for p in points]
