import logging
import uuid
from typing import Dict, List, Any

from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from qdrant_client.http.exceptions import UnexpectedResponse
from utils.errors import VectorDBError, DatabaseConnectionError

logger = logging.getLogger(__name__)


class VectorDBService:
    """Service for storing and searching CV data in Qdrant vector database"""

    def __init__(self, host: str, port: int, collection_name: str, vector_size: int):
        """Initialize the vector database service

        Args:
            host: Qdrant host address
            port: Qdrant port
            collection_name: Name of the vector collection
            vector_size: Dimensionality of vectors to store (384 for all-MiniLM-L6-v2)
        """
        try:
            self.client = QdrantClient(host=host, port=port)
            self.collection_name = collection_name
            self.vector_size = vector_size

            # Initialize collection if it doesn't exist
            self._initialize_collection()
            logger.info(f"Connected to Qdrant at {host}:{port}, collection: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {str(e)}")
            raise DatabaseConnectionError(f"Failed to connect to Qdrant: {str(e)}")

    def _initialize_collection(self) -> None:
        """Create collection if it doesn't exist"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]

            if self.collection_name not in collection_names:
                logger.info(f"Creating new collection '{self.collection_name}' with vector size {self.vector_size}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qdrant_models.VectorParams(
                        size=self.vector_size,
                        distance=qdrant_models.Distance.COSINE
                    )
                )

                # Create payload indexes for faster filtering
                self._create_payload_indexes()
        except Exception as e:
            logger.error(f"Failed to initialize collection: {str(e)}")
            raise VectorDBError(f"Failed to initialize vector collection: {str(e)}")

    def _create_payload_indexes(self) -> None:
        """Create indexes on frequently filtered fields"""
        try:
            # Create indexes for common fields used in filtering
            fields_to_index = ["cv_id", "person_name", "source"]
            for field in fields_to_index:
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field,
                    field_schema=qdrant_models.PayloadSchemaType.KEYWORD
                )
            logger.info(f"Created payload indexes for {', '.join(fields_to_index)}")
        except Exception as e:
            logger.warning(f"Failed to create payload indexes: {str(e)}")

    def store_vectors(self, cv_id: str, vectors: List[Dict[str, Any]]) -> List[str]:
        """Store pre-computed vectors, replacing any existing ones for this CV

        Args:
            cv_id: CV identifier
            vectors: List of vectors with metadata

        Returns:
            List of vector IDs
        """
        if not vectors:
            logger.warning(f"No vectors to store for CV {cv_id}")
            return []

        try:
            # First delete any existing vectors for this CV
            try:
                count = self.delete_cv_vectors(cv_id)
                if count > 0:
                    logger.info(f"Deleted {count} existing vectors for CV {cv_id}")
            except Exception as e:
                logger.warning(f"Error when attempting to delete existing vectors: {str(e)}")

            # Continue with vector storage
            points_to_insert = []

            for idx, vector_item in enumerate(vectors):
                # Generate a unique ID for each vector
                point_id = str(uuid.uuid4())

                # Extract the vector and validate
                vector = vector_item.get("vector")
                if not vector or not isinstance(vector, list):
                    logger.warning(f"Invalid vector format at index {idx} for CV {cv_id}")
                    continue

                if len(vector) != self.vector_size:
                    logger.warning(f"Vector dimension mismatch at index {idx} for CV {cv_id}: "
                                   f"Expected {self.vector_size}, got {len(vector)}")
                    continue

                # Prepare payload (all fields except 'vector')
                payload = {k: v for k, v in vector_item.items() if k != "vector"}
                payload["cv_id"] = cv_id

                # Create point for insertion
                points_to_insert.append(
                    qdrant_models.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload
                    )
                )

            # Insert in batches
            if points_to_insert:
                logger.info(f"Storing {len(points_to_insert)} vectors for CV {cv_id}")
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points_to_insert,
                    wait=True
                )

                return [p.id for p in points_to_insert]

            return []
        except Exception as e:
            logger.error(f"Error storing vectors: {str(e)}")
            raise VectorDBError(f"Failed to store vectors: {str(e)}")

    def delete_cv_vectors(self, cv_id: str) -> int:
        """Delete all vectors for a specific CV

        Args:
            cv_id: CV identifier

        Returns:
            Number of vectors deleted
        """
        try:
            filter_obj = qdrant_models.Filter(
                must=[
                    qdrant_models.FieldCondition(
                        key="cv_id",
                        match=qdrant_models.MatchValue(value=cv_id)
                    )
                ]
            )

            # Count existing points
            count_result = self.client.count(
                collection_name=self.collection_name,
                count_filter=filter_obj
            )
            count = count_result.count

            if count > 0:
                # Delete points
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=qdrant_models.FilterSelector(filter=filter_obj)
                )
                logger.info(f"Deleted {count} vectors for CV {cv_id}")

            return count

        except Exception as e:
            logger.error(f"Error deleting vectors for CV {cv_id}: {str(e)}")
            raise VectorDBError(f"Failed to delete vectors: {str(e)}")
