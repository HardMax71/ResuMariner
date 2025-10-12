import asyncio
import logging
import os
import time
from dataclasses import asdict

from django.conf import settings
from neomodel import adb

from core.database import create_graph_service, create_vector_service
from core.domain.extraction import ParsedDocument
from processor.models import CleanupTask, QueuedTask
from processor.services.processing_service import ProcessingService

from ..services.job_service import JobService
from ..utils.redis_queue import RedisJobQueue
from .base import BaseWorker


class ProcessingWorker(BaseWorker):
    def __init__(self):
        super().__init__()
        self.name = "processing"
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        self.job_service = JobService()
        self.redis_queue = RedisJobQueue()
        self.concurrent_jobs = int(os.environ.get("WORKER_CONCURRENT_JOBS", "3"))
        self.semaphore = asyncio.Semaphore(self.concurrent_jobs)
        self.graph_db = None
        self.vector_db = None
        self.processing_service = None
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
        uid: str = job_data.uid
        file_path: str = job_data.file_path

        start_time = time.time()

        try:
            self.logger.info("Processing job %s (task %s) - started instantly", uid, task_id)

            await self.redis_queue.mark_job_processing(task_id, uid)
            await self.job_service.mark_processing(uid)

            self.logger.info("Processing job %s", uid)

            # Extract parsed document from first-class field
            parsed_doc = ParsedDocument.from_dict(job_data.parsed_doc)

            result = await self.processing_service.process_resume(file_path=file_path, uid=uid, parsed_doc=parsed_doc)  # type: ignore[union-attr]

            result_dict = {
                "resume": result.resume.model_dump(),
                "review": result.review.model_dump() if result.review else None,
                "metadata": asdict(result.metadata),
            }

            await self.redis_queue.mark_job_completed(task_id, uid, result_dict)
            await self.job_service.complete(uid, result_dict)

            processing_time = time.time() - start_time
            self.logger.info("Job %s completed successfully in %.2fs", uid, processing_time)

            await self._schedule_cleanup(uid)

        except Exception as e:
            self.logger.exception("Job %s failed: %s", uid, e)
            await self.redis_queue.mark_job_failed(task_id, uid, str(e), retry=True)
            await self.job_service.fail(uid, str(e))

    async def _schedule_cleanup(self, uid: str):
        try:
            cleanup_delay = settings.JOB_CLEANUP_DELAY_HOURS
            cleanup_task = CleanupTask(uid=uid, cleanup_time=time.time() + (cleanup_delay * 3600))
            await self.redis_queue.schedule_cleanup(cleanup_task)
            self.logger.info("Scheduled cleanup for job %s in %d hours", uid, cleanup_delay)
        except Exception as e:
            self.logger.warning("Failed to schedule cleanup for job %s: %s", uid, e)

    async def startup(self):
        """Initialize services"""
        await self.redis_queue.get_redis()
        self.logger.info("Redis connections initialized")

        # Neo4j connection for this worker process
        host = settings.NEO4J_URI.replace("bolt://", "")
        connection_url = f"bolt://{settings.NEO4J_USERNAME}:{settings.NEO4J_PASSWORD}@{host}"
        await adb.set_connection(url=connection_url)

        # Create service instances
        self.graph_db = create_graph_service()
        self.vector_db = create_vector_service()
        self.processing_service = ProcessingService(self.graph_db, self.vector_db)

        self.logger.info("Processing worker ready")

    async def shutdown(self):
        """Clean shutdown"""
        self.running = False
        await self.redis_queue.close()
