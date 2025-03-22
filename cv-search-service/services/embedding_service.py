import logging
from typing import List, Optional, ClassVar

from config import settings
from sentence_transformers import SentenceTransformer
from utils.errors import EmbeddingError

logger = logging.getLogger(__name__)


class EmbeddingService:
    _instance: ClassVar[Optional['EmbeddingService']] = None
    model: SentenceTransformer
    vector_size: int

    def __new__(cls):
        """Singleton pattern to reuse the embedding model"""
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            try:
                cls._instance.model = SentenceTransformer(settings.EMBEDDING_MODEL)
                cls._instance.vector_size = cls._instance.model.get_sentence_embedding_dimension()
                logger.info(
                    f"Embedding model loaded: {settings.EMBEDDING_MODEL} "
                    f"with dimension {cls._instance.vector_size}")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {str(e)}")
                raise EmbeddingError(f"Failed to initialize embedding model: {str(e)}")
        return cls._instance

    def encode(self, text: str) -> List[float]:
        """Generate embedding vector for a text query"""
        try:
            if not text.strip():
                raise ValueError("Cannot encode empty text")

            vector = self.model.encode(text)
            return vector.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise EmbeddingError(f"Failed to generate embedding: {str(e)}")

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for multiple texts"""
        try:
            if not texts:
                return []

            vectors = self.model.encode(texts)
            return [vector.tolist() for vector in vectors]
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise EmbeddingError(f"Failed to generate batch embeddings: {str(e)}")
