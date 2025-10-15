import logging
import uuid

from rest_framework.exceptions import ValidationError

from core.services.graph_db_service import GraphDBService
from core.services.vector_db_service import VectorDBService

from ..models import Job
from ..utils.email_extractor import extract_email
from .file_service import FileService
from .job_service import JobService
from .parsing.parsing_service import ParsingService

logger = logging.getLogger(__name__)


class ResumeService:
    """Application-layer orchestration for resume operations.

    Coordinates business logic for resume upload and deletion workflows,
    delegating to infrastructure services (JobService, GraphDBService, etc.).
    """

    def __init__(self, job_service: JobService, graph_db: GraphDBService, vector_db: VectorDBService) -> None:
        self.job_service = job_service
        self.graph_db = graph_db
        self.vector_db = vector_db

    async def upload_resume(self, file_content: bytes, filename: str) -> Job:
        """Handle resume upload workflow.

        Orchestrates: file validation, parsing, duplicate check, job creation, and enqueueing.

        Args:
            file_content: Resume file bytes
            filename: Original filename

        Returns:
            Job object tracking processing status

        Raises:
            ValidationError: If email not found or resume already exists
        """
        uid = str(uuid.uuid4())

        try:
            temp_path = await FileService.save_validated_content(file_content, filename, uid)

            parser = ParsingService()
            parsed_doc = await parser.parse_file(temp_path)

            email = extract_email(parsed_doc)
            if not email:
                logger.warning("Resume upload failed: no email found in file %s", filename)
                raise ValidationError("Cannot process resume without email address")

            existing = await self.graph_db.get_resume_by_email(email)
            if existing:
                logger.warning("Resume upload failed: email %s already exists with uid %s", email, existing.uid)
                raise ValidationError("Resume with this email already exists")

            job = await self.job_service.create_job(file_path=temp_path, uid=uid)
            execution_id = await self.job_service.enqueue_job(uid, temp_path, parsed_doc.to_dict())
            logger.info("Job %s queued for async processing with execution_id %s", uid, execution_id)

            return job

        except Exception:
            await FileService.cleanup_all_job_files(uid)
            raise

    async def delete_resume(self, uid: str) -> None:
        """Delete resume and all associated data.

        Orchestrates: graph DB deletion, vector DB deletion, file cleanup, and job deletion.

        Args:
            uid: Resume/job unique identifier
        """
        job = await self.job_service.get_job(uid)

        try:
            deleted = await self.graph_db.delete_resume(job.uid)
            if deleted:
                logger.info("Deleted resume %s from graph DB", job.uid)
            else:
                logger.warning("Resume %s not found in graph DB", job.uid)
        except Exception as e:
            logger.error("Failed to delete resume %s from graph DB: %s", job.uid, e)

        try:
            count = await self.vector_db.delete_resume_vectors(job.uid)
            logger.info("Deleted %d vectors for resume %s", count, job.uid)
        except Exception as e:
            logger.error("Failed to delete vectors for resume %s: %s", job.uid, e)

        await FileService.cleanup_all_job_files(uid)
        logger.info("Deleted files for job %s", uid)

        await self.job_service.delete_job(uid)
        logger.info("Deleted job %s from Redis", uid)
