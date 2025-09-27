import asyncio
import logging
import os
import time
from dataclasses import asdict

from django.conf import settings

from processor.models import QueuedTask
from processor.services.processing_service import ProcessingService

from ..services.job_service import JobService
from ..utils.redis_queue import RedisJobQueue
from .base import BaseWorker


class ProcessingWorker(BaseWorker):
    def __init__(self):
        super().__init__()
        self.name = "processing"
        self.sleep_interval = 1.0
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        self.job_service = JobService()
        self.processing_service = ProcessingService()
        self.redis_queue = RedisJobQueue()
        self.concurrent_jobs = int(os.environ.get("WORKER_CONCURRENT_JOBS", "3"))
        self.active_tasks: set[asyncio.Task] = set()
        self.logger.info(f"Initialized processing worker with {self.concurrent_jobs} concurrent job slots")

    async def process_iteration(self) -> bool:
        self.redis_queue.process_retries()

        # Clean up completed tasks
        done_tasks = {task for task in self.active_tasks if task.done()}
        for task in done_tasks:
            self.active_tasks.discard(task)
            # Await task to get any exceptions that occurred
            try:
                await task
            except Exception as e:
                self.logger.error(f"Task failed with exception: {e}")

        # Check if we have capacity for more jobs
        if len(self.active_tasks) >= self.concurrent_jobs:
            return False

        # Try to get a job from the queue
        job_data = self.redis_queue.get_next_job()
        if not job_data:
            return False

        # Process job asynchronously
        task = asyncio.create_task(self._process_job(job_data))
        self.active_tasks.add(task)

        return True

    async def _process_job(self, job_data: QueuedTask) -> None:
        task_id: str = job_data.task_id
        job_id: str = job_data.job_id
        file_path: str = job_data.file_path

        start_time = time.time()

        try:
            self.logger.info("Processing job %s (task %s)", job_id, task_id)

            self.redis_queue.mark_job_processing(task_id)
            await self.job_service.mark_processing(job_id)

            result = await self.processing_service.process_resume(
                file_path=file_path,
                job_id=job_id
            )

            # Convert ProcessingResult to dict for storage
            result_dict = {
                "resume": result.resume.model_dump(),
                "review": result.review.model_dump() if result.review else None,  # ReviewResult is Pydantic model
                "metadata": asdict(result.metadata)
            }

            self.redis_queue.mark_job_completed(task_id, result_dict)
            await self.job_service.complete(job_id, result_dict)

            processing_time = time.time() - start_time
            self.logger.info(
                "Job %s completed successfully in %.2fs",
                job_id,
                processing_time
            )

            self._schedule_cleanup(job_id)

        except Exception as e:
            self.logger.exception("Job %s failed: %s", job_id, e)
            self.redis_queue.mark_job_failed(task_id, str(e), retry=True)
            await self.job_service.fail(job_id, str(e))

    def _schedule_cleanup(self, job_id: str):
        try:
            from processor.models import CleanupTask
            cleanup_delay = settings.JOB_CLEANUP_DELAY_HOURS
            cleanup_task = CleanupTask(
                job_id=job_id,
                cleanup_time=time.time() + (cleanup_delay * 3600)
            )
            self.redis_queue.schedule_cleanup(cleanup_task)
            self.logger.info(
                "Scheduled cleanup for job %s in %d hours",
                job_id,
                cleanup_delay
            )
        except Exception as e:
            self.logger.warning("Failed to schedule cleanup for job %s: %s", job_id, e)

    async def startup(self):
        """No async initialization needed."""
        pass

    async def shutdown(self):
        """Wait for active tasks to complete."""
        if self.active_tasks:
            self.logger.info("Waiting for %d active tasks to complete", len(self.active_tasks))
            await asyncio.gather(*self.active_tasks, return_exceptions=True)
