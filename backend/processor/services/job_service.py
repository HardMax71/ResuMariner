import logging
import uuid
from datetime import datetime, timedelta

import redis.asyncio as redis
from django.conf import settings

from ..models import Job
from ..serializers import JobStatus
from ..utils.redis_queue import RedisJobQueue

logger = logging.getLogger(__name__)


class JobService:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )
        self.prefix = settings.REDIS_JOB_PREFIX
        self.ttl = timedelta(days=settings.JOB_RETENTION_DAYS)
        self.retention_days = settings.JOB_RETENTION_DAYS
        self.redis_queue = RedisJobQueue()

    def _get_key(self, job_id: str) -> str:
        return f"{self.prefix}{job_id}"

    async def create_job(self, file_path: str) -> Job:
        """Create a new job entry."""
        job_id = str(uuid.uuid4())
        job = Job(job_id=job_id, file_path=file_path)

        await self.redis.set(self._get_key(job_id), job.model_dump_json(), ex=int(self.ttl.total_seconds()))

        logger.info(f"Created job {job_id} for file {file_path}")
        return job

    async def get_job(self, job_id: str) -> Job | None:
        job_json = await self.redis.get(self._get_key(job_id))
        if not job_json:
            logger.warning(f"Job {job_id} not found")
            return None

        return Job.model_validate_json(job_json)

    async def list_jobs(self, limit: int = 100) -> list[Job]:
        """List all jobs in Redis."""
        jobs: list[Job] = []
        pattern = f"{self.prefix}*"
        cursor = 0

        while len(jobs) < limit:
            cursor, keys = await self.redis.scan(cursor=cursor, match=pattern, count=min(100, limit - len(jobs)))

            for key in keys:
                job_json = await self.redis.get(key)
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
        job_id: str,
        status: JobStatus,
        updates: dict | None = None,
        result: dict | None = None,
        error: str | None = None,
    ) -> Job | None:
        job = await self.get_job(job_id)
        if not job:
            logger.warning(f"Failed to update job {job_id} - not found")
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

        await self.redis.set(self._get_key(job_id), job.model_dump_json(), ex=int(self.ttl.total_seconds()))

        return job

    async def mark_processing(self, job_id: str) -> Job | None:
        return await self.update_job(job_id, status=JobStatus.PROCESSING)

    async def complete(self, job_id: str, result: dict) -> Job | None:
        return await self.update_job(job_id, status=JobStatus.COMPLETED, result=result)

    async def fail(self, job_id: str, error: str) -> Job | None:
        return await self.update_job(job_id, status=JobStatus.FAILED, error=error)

    async def save_job(self, job: Job) -> None:
        await self.redis.set(self._get_key(job.job_id), job.model_dump_json(), ex=int(self.ttl.total_seconds()))

    async def delete_job(self, job_id: str) -> bool:
        result = await self.redis.delete(self._get_key(job_id))
        success = result > 0

        if success:
            logger.info(f"Deleted job {job_id}")
        else:
            logger.warning(f"Failed to delete job {job_id}")

        return success

    async def process_job(self, job_id: str) -> dict:
        job = await self.get_job(job_id)
        if not job:
            raise Exception(f"Job not found: {job_id}")

        task_data = {"job_id": job_id, "file_path": job.file_path}
        task_id = self.redis_queue.enqueue_job(job_id, job.file_path, task_data)

        await self.update_job(job_id, status=JobStatus.PENDING, updates={"result": {"task_id": task_id}})
        logger.info(f"Job {job_id} queued for async processing with task_id {task_id}")

        return {"job_id": job_id, "status": "queued for async processing", "task_id": task_id}
