import asyncio
import logging
import os
import time
from dataclasses import asdict

from django.conf import settings

from processor.models import QueuedTask
from processor.services.processing_service import ProcessingService
from storage.services.graph_db_service import GraphDBService
from storage.services.vector_db_service import VectorDBService

from ..services.job_service import JobService
from ..utils.redis_queue import RedisJobQueue
from .base import BaseWorker


class ProcessingWorker(BaseWorker):
    def __init__(self):
        super().__init__()
        self.name = "processing"
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        self.job_service = JobService()
        self.processing_service = ProcessingService()
        self.redis_queue = RedisJobQueue()
        self.concurrent_jobs = int(os.environ.get("WORKER_CONCURRENT_JOBS", "3"))
        self.semaphore = asyncio.Semaphore(self.concurrent_jobs)
        self.logger.info(f"Initialized processing worker with {self.concurrent_jobs} concurrent job slots")

    async def create_tasks(self) -> list[asyncio.Task]:
        """Create all worker tasks that run concurrently"""
        return [
            asyncio.create_task(self.job_consumer()),
            asyncio.create_task(self.retry_listener()),
        ]

    async def job_consumer(self):
        """Consume jobs from Redis stream with zero delay"""
        self.logger.info("Starting job consumer")

        async for job_data in self.redis_queue.consume_jobs():
            if not self.running:
                break

            # Use semaphore to limit concurrent jobs
            asyncio.create_task(self._process_job_with_semaphore(job_data))

    async def _process_job_with_semaphore(self, job_data: QueuedTask):
        """Process job with concurrency limit"""
        async with self.semaphore:
            await self._process_job(job_data)

    async def retry_listener(self):
        """Listen for retry events"""
        self.logger.info("Starting retry listener")
        try:
            await self.redis_queue.listen_for_retries()
        except Exception as e:
            self.logger.error(f"Retry listener error: {e}")

    async def _process_job(self, job_data: QueuedTask) -> None:
        task_id: str = job_data.task_id
        job_id: str = job_data.job_id
        file_path: str = job_data.file_path

        start_time = time.time()

        try:
            self.logger.info("Processing job %s (task %s) - started instantly", job_id, task_id)

            await self.redis_queue.mark_job_processing(task_id, job_id)
            await self.job_service.mark_processing(job_id)

            result = await self.processing_service.process_resume(file_path=file_path, job_id=job_id)

            result_dict = {
                "resume": result.resume.model_dump(),
                "review": result.review.model_dump() if result.review else None,
                "metadata": asdict(result.metadata),
            }

            await self.redis_queue.mark_job_completed(task_id, job_id, result_dict)
            await self.job_service.complete(job_id, result_dict)

            processing_time = time.time() - start_time
            self.logger.info("Job %s completed successfully in %.2fs", job_id, processing_time)

            await self._schedule_cleanup(job_id)

        except Exception as e:
            self.logger.exception("Job %s failed: %s", job_id, e)
            await self.redis_queue.mark_job_failed(task_id, job_id, str(e), retry=True)
            await self.job_service.fail(job_id, str(e))

    async def _schedule_cleanup(self, job_id: str):
        try:
            from processor.models import CleanupTask

            cleanup_delay = settings.JOB_CLEANUP_DELAY_HOURS
            cleanup_task = CleanupTask(job_id=job_id, cleanup_time=time.time() + (cleanup_delay * 3600))
            await self.redis_queue.schedule_cleanup(cleanup_task)
            self.logger.info("Scheduled cleanup for job %s in %d hours", job_id, cleanup_delay)
        except Exception as e:
            self.logger.warning("Failed to schedule cleanup for job %s: %s", job_id, e)

    async def startup(self):
        """Initialize Redis and database connections"""
        await self.redis_queue.get_redis()
        self.logger.info("Redis connections initialized")

        await GraphDBService.configure()
        self.logger.info("GraphDBService configured")

        await VectorDBService.configure()
        self.logger.info("VectorDBService configured")

    async def shutdown(self):
        """Clean shutdown"""
        self.running = False
        await self.redis_queue.close()
