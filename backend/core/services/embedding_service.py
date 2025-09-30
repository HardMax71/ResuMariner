import logging
import time

import httpx
from django.conf import settings

from core.metrics import EMBEDDING_API_CALLS, EMBEDDING_API_DURATION
from processor.utils.circuit_breaker import create_custom_circuit_breaker

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Unified embedding service for all embedding operations.
    Optimized for batch operations to minimize API calls.
    """

    def __init__(self, model_name: str | None = None):
        """
        Initialize the embedding service.

        Args:
            model_name: Optional model name override. Defaults to settings.EMBEDDING_MODEL
        """
        self.model = model_name or settings.EMBEDDING_MODEL
        self.endpoint = self._build_endpoint()
        self.headers = self._build_headers()
        self.timeout = 60.0
        self.batch_timeout = 120.0
        self.max_batch_size = 64  # OpenAI recommends chunking for reliability
        self._validate_config()

        self.circuit_breaker = create_custom_circuit_breaker(
            name="embedding_api", fail_max=3, reset_timeout=30, exclude=[httpx.InvalidURL]
        )

    def _validate_config(self):
        if not settings.TEXT_LLM_API_KEY:
            raise ValueError("LLM_API_KEY is required for embeddings")
        if not self.model:
            raise ValueError("EMBEDDING_MODEL is required")

    def _build_endpoint(self) -> str:
        base = settings.TEXT_LLM_BASE_URL or "https://api.openai.com/v1"
        return f"{base.rstrip('/')}/embeddings"

    def _build_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {settings.TEXT_LLM_API_KEY}",
            "Content-Type": "application/json",
        }

    def encode(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.
        Use this only for single texts (e.g., search queries).
        For multiple texts, use encode_batch() for efficiency.

        Args:
            text: Text to encode

        Returns:
            Embedding vector as list of floats

        Raises:
            ValueError: If text is empty
            httpx.HTTPError: If API call fails
        """
        if not text or not text.strip():
            raise ValueError("Cannot encode empty text")

        # For single text, just call batch with one item
        embeddings = self.encode_batch([text])
        return embeddings[0]

    def encode_batch(self, texts: list[str], skip_empty: bool = True) -> list[list[float]]:
        """
        Batch encode multiple texts efficiently.
        This should be the primary method for encoding multiple texts.

        Args:
            texts: List of texts to encode
            skip_empty: Whether to skip empty texts (default: True)

        Returns:
            List of embedding vectors. Empty texts are skipped if skip_empty=True.

        Note:
            Makes minimal API calls by batching up to 64 texts per request.
        """
        if not texts:
            return []

        # Filter and prepare texts
        valid_texts = []
        for i, text in enumerate(texts):
            if text and text.strip():
                valid_texts.append(text.strip())
            elif not skip_empty:
                logger.warning("Empty text at index %d skipped", i)

        if not valid_texts:
            return []

        batch_size_label = "large" if len(valid_texts) > 20 else "small"

        start_time = time.time()
        embeddings = []

        # Process in chunks for API limits and reliability
        for i in range(0, len(valid_texts), self.max_batch_size):
            chunk = valid_texts[i : i + self.max_batch_size]

            payload = {"model": self.model, "input": chunk}

            chunk_embeddings = self.circuit_breaker(self._call_embedding_api)(payload, len(chunk))
            embeddings.extend(chunk_embeddings)
            logger.debug("Encoded batch of %d texts", len(chunk))

        # Record the duration
        EMBEDDING_API_DURATION.labels(batch_size=batch_size_label).observe(time.time() - start_time)
        return embeddings

    def _call_embedding_api(self, payload: dict, batch_size: int) -> list[list[float]]:
        """
        Make API call to embedding service with circuit breaker protection.

        Args:
            payload: Request payload with model and input
            batch_size: Size of the batch being processed

        Returns:
            List of embedding vectors

        Raises:
            pybreaker.CircuitBreakerError: When circuit is open
            httpx.HTTPError: On API errors
        """
        try:
            with httpx.Client(timeout=self.batch_timeout) as client:
                resp = client.post(self.endpoint, headers=self.headers, json=payload)
                resp.raise_for_status()
                data = resp.json()

                batch_label = "large" if batch_size > 20 else "small"
                EMBEDDING_API_CALLS.labels(status="success", batch_size=batch_label).inc()
                return [item["embedding"] for item in data["data"]]
        except Exception:
            batch_label = "large" if batch_size > 20 else "small"
            EMBEDDING_API_CALLS.labels(status="error", batch_size=batch_label).inc()
            raise
