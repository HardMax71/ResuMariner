import logging
import re
import uuid
from datetime import datetime
from typing import Any

import redis.asyncio as aioredis
from django.conf import settings

from core.domain.extraction import ParsedDocument

from ..models import Job
from ..serializers import JobStatus
from ..utils.redis_queue import RedisJobQueue
from .file_service import FileService
from .parsing.parsing_service import ParsingService

logger = logging.getLogger(__name__)


class JobService:
    def __init__(self):
        self.redis_pool = aioredis.ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            max_connections=20,
            decode_responses=True,
        )
        self.prefix = settings.REDIS_JOB_PREFIX
        self.redis_queue = RedisJobQueue()

    async def _get_redis(self) -> aioredis.Redis:
        return aioredis.Redis(connection_pool=self.redis_pool)

    def _get_key(self, uid: str) -> str:
        return f"{self.prefix}{uid}"

    @staticmethod
    def _extract_email(parsed_doc: ParsedDocument) -> str | None:
        """Extract first valid email from parsed document."""
        EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9][A-Za-z0-9._%+-]*@[A-Za-z0-9][A-Za-z0-9.-]*\.[A-Z|a-z]{2,}\b")

        link_urls = " ".join(link.url for page in parsed_doc.pages for link in page.links)
        page_text = " ".join(filter(None, [page.text for page in parsed_doc.pages]))
        combined_text = link_urls + " " + page_text

        match = EMAIL_PATTERN.search(combined_text)
        return match.group(0).lower() if match else None

    async def create_job(self, file_path: str, uid: str) -> Job:
        """Create a new job entry."""
        job = Job(uid=uid, file_path=file_path)
        redis = await self._get_redis()
        await redis.set(self._get_key(uid), job.model_dump_json(), ex=settings.REDIS_PROCESSING_JOB_TTL)
        logger.info(f"Created job {uid}")
        return job

    async def get_job(self, uid: str) -> Job | None:
        redis = await self._get_redis()
        job_json = await redis.get(self._get_key(uid))
        if not job_json:
            logger.warning(f"Job {uid} not found")
            return None
        return Job.model_validate_json(job_json)

    async def list_jobs(self, limit: int = 100) -> list[Job]:
        """List all jobs in Redis."""
        jobs: list[Job] = []
        pattern = f"{self.prefix}*"
        cursor = 0
        redis = await self._get_redis()

        while len(jobs) < limit:
            cursor, keys = await redis.scan(cursor=cursor, match=pattern, count=min(100, limit - len(jobs)))

            for key in keys:
                job_json = await redis.get(key)
                if job_json:
                    job = Job.model_validate_json(job_json)
                    jobs.append(job)

                    if len(jobs) >= limit:
                        break

            if cursor == 0:
                break

        return jobs

    async def update_job(
        self,
        uid: str,
        status: JobStatus,
        updates: dict | None = None,
        result: dict | None = None,
        error: str | None = None,
    ) -> Job | None:
        job = await self.get_job(uid)
        if not job:
            logger.warning(f"Failed to update job {uid} - not found")
            return None

        changes: dict = {"updated_at": datetime.now()}
        if updates:
            changes.update(updates)
        if status is not None:
            changes["status"] = status
        if result is not None:
            changes["result"] = result
        if error is not None:
            changes["error"] = error
        if status in (JobStatus.COMPLETED, JobStatus.FAILED):
            changes["completed_at"] = datetime.now()

        job.update(**changes)
        redis = await self._get_redis()
        await redis.set(self._get_key(uid), job.model_dump_json(), ex=settings.REDIS_PROCESSING_JOB_TTL)
        return job

    async def mark_processing(self, uid: str) -> Job | None:
        return await self.update_job(uid, status=JobStatus.PROCESSING)

    async def complete(self, uid: str, result: dict) -> Job | None:
        return await self.update_job(uid, status=JobStatus.COMPLETED, result=result)

    async def fail(self, uid: str, error: str) -> Job | None:
        return await self.update_job(uid, status=JobStatus.FAILED, error=error)

    async def save_job(self, job: Job) -> None:
        redis = await self._get_redis()
        await redis.set(self._get_key(job.uid), job.model_dump_json(), ex=settings.REDIS_PROCESSING_JOB_TTL)

    async def delete_job(self, uid: str) -> bool:
        redis = await self._get_redis()
        result = await redis.delete(self._get_key(uid))
        success = result > 0

        if success:
            logger.info(f"Deleted job {uid}")
        else:
            logger.warning(f"Failed to delete job {uid}")

        return success

    async def delete_job_complete(self, uid: str, graph_db, vector_db) -> dict[str, Any]:
        result: dict[str, Any] = {
            "job_deleted": False,
            "resume_deleted": False,
            "vectors_deleted": 0,
            "file_deleted": False,
            "errors": [],
        }

        job = await self.get_job(uid)
        if not job:
            result["errors"].append(f"Job {uid} not found")
            return result

        deleted = await graph_db.delete_resume(job.uid)
        result["resume_deleted"] = deleted
        if deleted:
            logger.info(f"Deleted resume {job.uid} from graph DB")
        else:
            result["errors"].append(f"Resume {job.uid} not found in graph DB")

        count = await vector_db.delete_resume_vectors(job.uid)
        result["vectors_deleted"] = count
        logger.info(f"Deleted {count} vectors for resume {job.uid}")

        await FileService.cleanup_all_job_files(uid)
        result["file_deleted"] = True
        logger.info(f"Deleted file for job {uid}")

        result["job_deleted"] = await self.delete_job(uid)
        return result

    async def upload_resume(self, file_content: bytes, filename: str, graph_db) -> dict[str, Any]:
        """Handle resume upload workflow."""
        uid = str(uuid.uuid4())

        try:
            temp_path = await FileService.save_validated_content(file_content, filename, uid)

            parser = ParsingService()
            parsed_doc = await parser.parse_file(temp_path)

            email = self._extract_email(parsed_doc)
            if not email:
                await FileService.cleanup_all_job_files(uid)
                return {"error": "Cannot process resume without email address"}

            existing = await graph_db.get_resume_by_email(email)
            if existing:
                await FileService.cleanup_all_job_files(uid)
                return {"uid": existing.uid, "existing": True}

            job = await self.create_job(file_path=temp_path, uid=uid)
            await self.process_job(job.uid, parsed_doc)

            return {"uid": uid, "job": job}

        except Exception as e:
            logger.error(f"Resume upload failed: {e}")
            await FileService.cleanup_all_job_files(uid)
            raise

    async def process_job(self, uid: str, parsed_doc: ParsedDocument) -> dict:
        job = await self.get_job(uid)
        if not job:
            raise Exception(f"Job not found: {uid}")

        task_id = await self.redis_queue.enqueue_job(uid, job.file_path, parsed_doc.to_dict())

        await self.update_job(uid, status=JobStatus.PENDING, updates={"result": {"task_id": task_id}})
        logger.info(f"Job {uid} queued for async processing with task_id {task_id}")

        return {"uid": uid, "status": "queued for async processing", "task_id": task_id}

    async def close(self):
        """Close Redis connection pool"""
        await self.redis_pool.disconnect()
