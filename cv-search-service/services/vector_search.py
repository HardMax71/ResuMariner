import logging
from typing import List, Dict, Any, Optional

from config import settings
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from utils.errors import DatabaseError

logger = logging.getLogger(__name__)


class VectorSearchService:
    """Service for vector-based search in Qdrant"""

    def __init__(self):
        """Initialize the vector search service"""
        try:
            self.client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT
            )
            self.collection_name = settings.QDRANT_COLLECTION
            logger.info(f"Connected to Qdrant at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {str(e)}")
            raise DatabaseError(f"Vector database connection failed: {str(e)}")

    def search(self,
               query_vector: List[float],
               limit: int = 10,
               min_score: float = 0.0,
               filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        try:
            # Convert filters to Qdrant format
            filter_obj = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    if isinstance(value, list):
                        conditions.append(
                            qdrant_models.FieldCondition(
                                key=key,
                                match=qdrant_models.MatchAny(any=value)
                            )
                        )
                    else:
                        conditions.append(
                            qdrant_models.FieldCondition(
                                key=key,
                                match=qdrant_models.MatchValue(value=value)
                            )
                        )

                if conditions:
                    filter_obj = qdrant_models.Filter(must=conditions)

            # Execute search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=filter_obj,
                score_threshold=min_score
            )

            # Format results
            return [
                {
                    "cv_id": hit.payload.get("cv_id"),
                    "text": hit.payload.get("text"),
                    "person_name": hit.payload.get("person_name", "Unknown"),
                    "email": hit.payload.get("email", ""),
                    "source": hit.payload.get("source", "unknown"),
                    "context": hit.payload.get("context", ""),
                    "score": hit.score
                }
                for hit in results
            ]

        except Exception as e:
            logger.error(f"Error performing vector search: {str(e)}")
            raise DatabaseError(f"Vector search failed: {str(e)}")
