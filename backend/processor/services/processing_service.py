import logging

from django.conf import settings

from core.domain import (
    ProcessingMetadata,
    ProcessingResult,
    Resume,
    ReviewResult,
)
from core.domain.extraction import ParsedDocument
from core.services import EmbeddingService
from core.services.graph_db_service import GraphDBService
from core.services.vector_db_service import VectorDBService

from .content_structure_service import LLMContentStructureService
from .file_service import FileService
from .resume_embedding_extractor import ResumeEmbeddingExtractor
from .review_service import ReviewService

logger = logging.getLogger(__name__)


class ProcessingService:
    """Orchestrates complete resume processing pipeline: parsing, structuring, storage, and review."""

    def __init__(self, graph_db: GraphDBService, vector_db: VectorDBService) -> None:
        self.embedding_service = EmbeddingService()
        self.embedding_extractor = ResumeEmbeddingExtractor()
        self.graph_db = graph_db
        self.vector_db = vector_db
        logger.info("ProcessingService initialized")

    async def process_resume(
        self,
        file_path: str,
        uid: str,
        parsed_doc: ParsedDocument,
    ) -> ProcessingResult:
        """
        Process a resume file through the complete pipeline.

        Args:
            file_path: Path to resume file (local or s3:// prefix)
            uid: Unique identifier for both job and resume
            parsed_doc: Pre-parsed document from upload flow

        Returns:
            ProcessingResult with resume data, review, and metadata
        """
        file_info = await FileService.prepare_for_processing(file_path)
        resume = await self._structure_content(parsed_doc)

        resume = resume.model_copy(update={"uid": uid})

        metadata = ProcessingMetadata(
            filename=file_info.name, file_ext=file_info.ext, source=file_info.source, page_count=len(parsed_doc.pages)
        )

        if settings.WORKER_STORE_IN_DB:
            await self._store_to_databases(resume, uid, metadata)

        review = None
        if settings.WORKER_GENERATE_REVIEW:
            review = await self._generate_review(parsed_doc, resume, uid, metadata)

        return ProcessingResult(resume=resume, review=review, metadata=metadata)

    async def _structure_content(self, parsed_data: ParsedDocument) -> Resume:
        content_organizer = LLMContentStructureService(parsed_data)
        result = await content_organizer.structure_content()
        return result

    async def _store_to_databases(self, resume: Resume, uid: str, metadata: ProcessingMetadata) -> None:
        """
        Store resume in graph and vector databases.

        Updates metadata with storage results.
        """
        await self._store_to_graph(resume, uid, metadata)
        await self._store_embeddings(resume, uid, metadata)

    async def _store_to_graph(self, resume: Resume, uid: str, metadata: ProcessingMetadata) -> None:
        try:
            success = await self.graph_db.upsert_resume(resume)
            if success:
                metadata.graph_stored = True
                logger.info("Stored resume %s in Neo4j", uid)
            else:
                metadata.graph_error = "Graph storage returned failure"
                logger.error("Failed to store resume %s in Neo4j", uid)
        except Exception as e:
            metadata.graph_error = str(e)
            logger.error("Error storing resume %s in Neo4j: %s", uid, e)

    async def _store_embeddings(self, resume: Resume, uid: str, metadata: ProcessingMetadata) -> None:
        try:
            logger.info("Starting embedding storage for uid %s", uid)

            extracted_data = self.embedding_extractor.extract_for_embedding(resume)
            if not extracted_data.texts:
                logger.warning("No texts extracted for embedding from uid %s", uid)
                metadata.vector_stored = False
                metadata.vector_count = 0
                return

            logger.info("Encoding %d texts for uid %s", len(extracted_data.texts), uid)
            embeddings = self.embedding_service.encode_batch(extracted_data.texts)

            vectors = self.embedding_extractor.create_vectors(embeddings, extracted_data)

            logger.info("Storing %d vectors for uid %s", len(vectors), uid)
            stored_ids = await self.vector_db.store_vectors(uid, vectors)

            logger.info("Successfully stored %d vectors for uid %s", len(stored_ids), uid)
            metadata.vector_stored = True
            metadata.vector_count = len(stored_ids)
        except Exception as e:
            metadata.vector_error = str(e)
            metadata.vector_stored = False
            logger.error("Error storing vectors for uid %s: %s", uid, e)

    async def _generate_review(
        self, parsed_doc: ParsedDocument, resume: Resume, uid: str, metadata: ProcessingMetadata
    ) -> ReviewResult | None:
        try:
            review_service = ReviewService(parsed_doc, resume)
            review = await review_service.iterative_review()
            if not review:
                return None

            metadata.review_generated = True
            return review

        except Exception as e:
            logger.error("Error generating review for uid %s: %s", uid, e)
            metadata.review_error = str(e)
            metadata.review_generated = False
            return None
