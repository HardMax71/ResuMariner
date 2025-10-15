import asyncio
import logging
import os
import time
from dataclasses import asdict

from django.conf import settings
from neomodel import adb

from core.database import create_graph_service, create_vector_service
from core.domain.extraction import ParsedDocument
from processor.services.processing_service import ProcessingService

from ..models import JobExecution
from ..services.job_service import JobService
from .base import BaseWorker


class ProcessingWorker(BaseWorker):
    """Worker that consumes and processes resume jobs from Redis stream."""

    def __init__(self):
        super().__init__()
        self.name = "processing"
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        self.concurrent_jobs = int(os.environ.get("WORKER_CONCURRENT_JOBS", settings.WORKER_CONCURRENT_JOBS))
        self.semaphore = asyncio.Semaphore(self.concurrent_jobs)
        self.job_service = JobService()
        self.graph_db = None
        self.vector_db = None
        self.processing_service = None
        self.active_tasks: set[asyncio.Task] = set()
        self.logger.info("Initialized processing worker with %s concurrent job slots", self.concurrent_jobs)

    async def create_tasks(self) -> list[asyncio.Task]:
        """Create all worker tasks that run concurrently"""
        return [
            asyncio.create_task(self.job_consumer()),
            asyncio.create_task(self.retry_listener()),
        ]

    def _task_done_callback(self, task: asyncio.Task) -> None:
        self.active_tasks.discard(task)

        if task.cancelled():
            return

        try:
            task.result()
        except Exception as e:
            self.logger.exception("Unhandled exception in processing task: %s", e)

    async def job_consumer(self) -> None:
        self.logger.info("Starting job consumer")

        async for execution in self.job_service.consume_jobs():
            if not self.running:
                break

            async_task = asyncio.create_task(self._process_job_with_semaphore(execution))
            self.active_tasks.add(async_task)
            async_task.add_done_callback(self._task_done_callback)

    async def _process_job_with_semaphore(self, execution: JobExecution) -> None:
        async with self.semaphore:
            await self._process_job(execution)

    async def retry_listener(self) -> None:
        self.logger.info("Starting retry listener")
        try:
            await self.job_service.listen_for_retries()
        except Exception as e:
            self.logger.error("Retry listener error: %s", e)

    async def _process_job(self, execution: JobExecution) -> None:
        """Process a single execution attempt.

        Args:
            execution: The execution attempt to process
        """
        execution_id: str = execution.execution_id
        job_uid: str = execution.job_uid
        file_path: str = execution.file_path

        start_time = time.time()

        try:
            self.logger.info("Processing job %s (execution %s) - started instantly", job_uid, execution_id)

            await self.job_service.mark_execution_processing(execution_id, job_uid)

            self.logger.info("Processing job %s", job_uid)

            parsed_doc = ParsedDocument.from_dict(execution.parsed_doc)

            assert self.processing_service is not None, "ProcessingService not initialized"
            result = await self.processing_service.process_resume(
                file_path=file_path, uid=job_uid, parsed_doc=parsed_doc
            )

            result_dict = {
                "resume": result.resume.model_dump(),
                "review": result.review.model_dump() if result.review else None,
                "metadata": asdict(result.metadata),
            }

            await self.job_service.mark_execution_completed(execution_id, job_uid, result_dict)

            processing_time = time.time() - start_time
            self.logger.info("Job %s completed successfully in %.2fs", job_uid, processing_time)

        except Exception as e:
            self.logger.exception("Job %s failed: %s", job_uid, e)
            await self.job_service.mark_execution_failed(execution_id, job_uid, str(e), retry=True)

    async def startup(self) -> None:
        await JobService.initialize()
        await adb.set_connection(url=settings.NEO4J_URI)

        self.graph_db = create_graph_service()
        self.vector_db = create_vector_service()
        self.processing_service = ProcessingService(self.graph_db, self.vector_db)

        self.logger.info("Processing worker ready")

    async def shutdown(self) -> None:
        self.running = False

        if self.active_tasks:
            self.logger.info("Waiting for %d active tasks to complete", len(self.active_tasks))
            await asyncio.gather(*self.active_tasks, return_exceptions=True)
            self.logger.info("All active tasks completed")

        self.logger.info("Processing worker shutdown complete")
