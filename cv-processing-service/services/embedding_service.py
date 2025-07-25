import logging
from typing import List, Dict, Any

import httpx
from config import settings
from models.resume_models import ResumeStructure
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from utils.errors import EmbeddingServiceError


class EmbeddingService:
    """Service for generating embeddings from CV text data and sending to storage"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the embedding service with the specified model"""
        try:
            self.model = SentenceTransformer(model_name)
            self.storage_url = settings.STORAGE_SERVICE_URL
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            raise EmbeddingServiceError(
                f"Failed to initialize embedding service: {str(e)}"
            )

    def _create_embedding(
        self, text: Any, source: str, context: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any] | None:
        """Helper method to create a single embedding with metadata"""
        if not text:
            return None
        # If text is not a string, try to use its 'text' attribute or convert it.
        if not isinstance(text, str):
            text = getattr(text, "text", str(text))
        vector = self.model.encode(text).tolist()
        return {
            "vector": vector,
            "text": text,
            "source": source,
            "context": context,
            **metadata,
        }

    def _extract_fragments(
        self, obj: Any, path: List[str] | None = None
    ) -> List[Dict[str, Any]]:
        """
        Recursively traverse the resume structure to extract text fragments.
        Returns a list of dictionaries where each dictionary contains:
            - 'text': the text fragment,
            - 'source': the last field name,
            - 'context': the full hierarchical path (joined by ' > '),
            - 'metadata': additional metadata (here, the raw path list).
        """
        if path is None:
            path = []
        fragments = []

        if isinstance(obj, str):
            fragments.append(
                {
                    "text": obj,
                    "source": path[-1] if path else "root",
                    "context": " > ".join(path),
                    "metadata": {"path": path.copy()},
                }
            )
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                # Append a simple index representation
                fragments.extend(self._extract_fragments(item, path + [f"[{idx}]"]))
        elif isinstance(obj, dict):
            for key, value in obj.items():
                fragments.extend(self._extract_fragments(value, path + [key]))
        elif isinstance(obj, BaseModel):
            # Convert the model to a dict and then process its fields.
            data = obj.model_dump(exclude_unset=True, exclude_none=True)
            for key, value in data.items():
                fragments.extend(self._extract_fragments(value, path + [key]))
        else:
            # For other primitive types
            fragments.append(
                {
                    "text": str(obj),
                    "source": path[-1] if path else "root",
                    "context": " > ".join(path),
                    "metadata": {"path": path.copy()},
                }
            )
        return fragments

    def generate_embeddings(self, resume: ResumeStructure) -> List[Dict[str, Any]]:
        """Generate embeddings for all text fragments extracted from the resume."""
        try:
            embeddings = []
            # Define base metadata from core personal info.
            base_metadata = {
                "person_name": resume.personal_info.name,
                "email": resume.personal_info.contact.email,
            }
            # Extract all text fragments recursively.
            fragments = self._extract_fragments(resume)
            self.logger.info(f"Extracted {len(fragments)} text fragments from resume")
            for frag in fragments:
                # Merge base metadata with fragment metadata.
                merged_metadata = {**base_metadata, **frag.get("metadata", {})}
                emb = self._create_embedding(
                    text=frag["text"],
                    source=frag["source"],
                    context=frag["context"],
                    metadata=merged_metadata,
                )
                if emb:
                    embeddings.append(emb)
            self.logger.info(f"Generated {len(embeddings)} embeddings for CV")
            return embeddings
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {str(e)}")
            raise EmbeddingServiceError(f"Failed to generate embeddings: {str(e)}")

    async def send_embeddings_to_storage(
        self, cv_id: str, resume: ResumeStructure
    ) -> bool:
        """Generate embeddings and send to storage service"""
        try:
            embeddings = self.generate_embeddings(resume)
            if not embeddings:
                self.logger.warning(f"No embeddings generated for CV {cv_id}")
                return False
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.storage_url}/vectors",
                    json={"cv_id": cv_id, "vectors": embeddings},
                    timeout=60.0,
                )
                if response.status_code != 200:
                    self.logger.error(f"Failed to store embeddings: {response.text}")
                    return False
                self.logger.info(
                    f"Successfully stored {len(embeddings)} embeddings for CV {cv_id}"
                )
                return True
        except Exception as e:
            self.logger.error(f"Error sending embeddings to storage: {str(e)}")
            return False
