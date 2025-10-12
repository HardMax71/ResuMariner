import logging
import os
from pathlib import Path

from django.conf import settings

from core.domain import (
    EmbeddingTextData,
    EmbeddingVector,
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
from .review_service import ReviewService

logger = logging.getLogger(__name__)


class ProcessingService:
    def __init__(self, graph_db: GraphDBService, vector_db: VectorDBService) -> None:
        self.embedding_service = EmbeddingService(settings.EMBEDDING_MODEL)
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
        file_path, source = await self._prepare_file_path(file_path)
        file_info = self._validate_file(file_path)
        resume = await self._structure_content(parsed_doc)

        resume = resume.model_copy(update={"uid": uid})

        # Create metadata
        metadata = ProcessingMetadata(
            filename=file_info["name"], file_ext=file_info["ext"], source=source, page_count=len(parsed_doc.pages)
        )

        if settings.WORKER_STORE_IN_DB:
            await self._store_to_databases(resume, uid, metadata)

        review = None
        if settings.WORKER_GENERATE_REVIEW:
            review = await self._generate_review(parsed_doc, resume, uid, metadata)

        return ProcessingResult(resume=resume, review=review, metadata=metadata)

    async def _prepare_file_path(self, file_path: str) -> tuple[str, str]:
        """
        Prepare file path and determine source.

        Returns:
            Tuple of (actual_file_path, source_type)
        """
        if file_path.startswith("s3:"):
            s3_key = file_path[3:]
            return await FileService.download_from_s3_async(s3_key), "s3"
        return file_path, "local"

    def _validate_file(self, file_path: str) -> dict[str, str]:
        """
        Validate file exists and has proper extension.

        Returns:
            Dict with filename and extension
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        path = Path(file_path)
        if not path.name:
            raise ValueError("File name is missing")

        if not path.suffix:
            raise ValueError(f"Invalid file name or missing extension: {path.name}")

        return {"name": path.name, "ext": path.suffix.lower()}

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
                raise Exception(f"Failed to store resume {uid} in Neo4j")
        except Exception as e:
            metadata.graph_error = str(e)
            logger.error("Error storing resume %s in Neo4j: %s", uid, e)
            raise

    async def _store_embeddings(self, resume: Resume, uid: str, metadata: ProcessingMetadata) -> None:
        try:
            logger.info("Starting embedding storage for uid %s", uid)
            vectors = self._generate_embeddings_from_resume(resume)
            if not vectors:
                logger.warning("No vectors generated for uid %s", uid)
                metadata.vector_stored = False
                metadata.vector_count = 0
                return

            logger.info("Storing %d vectors for uid %s", len(vectors), uid)
            stored_ids = await self.vector_db.store_vectors(uid, vectors)

            logger.info("Successfully stored %d vectors for uid %s", len(stored_ids), uid)
            metadata.vector_stored = True
            metadata.vector_count = len(stored_ids)
        except Exception as e:
            metadata.vector_error = str(e)
            metadata.vector_stored = False
            logger.error("Error storing vectors for uid %s: %s", uid, e)
            raise

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

    def _generate_embeddings_from_resume(self, resume: Resume) -> list[EmbeddingVector]:
        text_data_list = self._extract_texts_for_embedding(resume)

        logger.info("Extracted %d texts for embedding from resume %s", len(text_data_list), resume.uid)

        if not text_data_list:
            logger.warning("No texts to encode for resume %s", resume.uid)
            return []

        texts = [item.text for item in text_data_list]

        logger.info("Encoding %d texts in batch for resume", len(texts))
        embeddings = self.embedding_service.encode_batch(texts)

        # Extract metadata for search filtering (all lists are guaranteed to exist)
        all_skills = [s.name for s in resume.skills]
        all_skills.extend(s.name for emp in resume.employment_history for s in emp.skills)
        all_skills.extend(s.name for proj in resume.projects for s in proj.skills)

        # Only include fields that EmbeddingVector expects
        vector_metadata = {
            "name": resume.personal_info.name,
            "email": resume.personal_info.contact.email,
            "skills": list(set(all_skills)),  # dedupe all skills from everywhere
            "companies": list({emp.company.name for emp in resume.employment_history if emp.company}),
            "role": resume.professional_profile.preferences.role
            if resume.professional_profile and resume.professional_profile.preferences
            else None,
            "location": resume.personal_info.demographics.current_location.city
            if resume.personal_info.demographics and resume.personal_info.demographics.current_location
            else None,
            "years_experience": sum(emp.duration.duration_months for emp in resume.employment_history) // 12,
        }

        vectors = [
            EmbeddingVector(
                vector=embedding,
                text=text_data.text,
                source=text_data.source,
                context=text_data.context,
                **vector_metadata,  # type: ignore[arg-type]
            )
            for embedding, text_data in zip(embeddings, text_data_list, strict=False)
        ]

        logger.info("Generated %d embedding vectors from resume", len(vectors))
        return vectors

    def _extract_texts_for_embedding(self, resume: Resume) -> list[EmbeddingTextData]:
        results: list[EmbeddingTextData] = []

        if resume.professional_profile and resume.professional_profile.summary:
            results.append(EmbeddingTextData(resume.professional_profile.summary, "summary", None))

        results.extend(EmbeddingTextData(s.name, "skill", None) for s in resume.skills)

        for employment in resume.employment_history:
            results.extend(
                EmbeddingTextData(kp.text, "employment", employment.position) for kp in employment.key_points
            )

        for project in resume.projects:
            results.extend(EmbeddingTextData(kp.text, "project", project.title) for kp in (project.key_points or []))

        for edu in resume.education:
            inst = edu.institution.name
            context = f"{edu.qualification} at {inst}" if edu.qualification else inst
            results.extend(EmbeddingTextData(ex.text, "education", context) for ex in (edu.extras or []))

        return results
