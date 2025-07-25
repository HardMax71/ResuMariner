import asyncio
import logging
import signal
import sys
import time
from typing import Dict, Any

from services.processing_service import ProcessingService
from services.file_service import FileService
from services.job_service import JobService
from models.job import JobStatus
from utils.redis_queue import redis_queue
from utils.monitoring import (
    record_job_metrics,
    record_error_metrics,
)
from utils.logger import set_request_context, clear_request_context
from utils.logger import setup_logging
from config import settings

logger = logging.getLogger(__name__)


class CVProcessingWorker:
    """Redis-based CV processing worker"""

    def __init__(self):
        self.running = False
        self.job_service = JobService()

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False

    async def start(self):
        """Start the worker"""
        setup_logging("cv-worker", settings.LOG_LEVEL)
        logger.info("Starting CV processing worker")

        self.running = True

        while self.running:
            try:
                # Process scheduled retries
                retries_processed = redis_queue.process_retries()
                if retries_processed > 0:
                    logger.info(f"Processed {retries_processed} retry jobs")

                # Get next job from queue
                job_data = redis_queue.dequeue_job()
                if not job_data:
                    continue

                await self._process_job(job_data)

            except Exception as e:
                logger.error(f"Worker error: {str(e)}")
                await asyncio.sleep(5)

        logger.info("Worker stopped")

    async def _process_job(self, job_data: Dict[str, Any]):
        """Process a single job"""
        task_id = job_data["task_id"]
        job_id = job_data["job_id"]
        file_path = job_data["file_path"]

        set_request_context(job_id=job_id, task_id=task_id)
        start_time = time.time()

        try:
            logger.info(f"Processing job {job_id} (task {task_id})")

            # Mark as processing
            redis_queue.mark_job_processing(task_id)
            await self.job_service.update_job_status(job_id, JobStatus.PROCESSING)
            record_job_metrics("cv-worker", "processing", "cv_processing")

            # Process CV
            result = await ProcessingService.process_cv(file_path, job_id)

            # Store processed data
            storage_result = await ProcessingService.store_cv_data(job_id, result)

            # Combine results
            final_result = {**result, "storage_info": storage_result}

            # Mark as completed
            redis_queue.mark_job_completed(task_id, final_result)
            await self.job_service.update_job_result(job_id, final_result)
            await self.job_service.update_job_status(job_id, JobStatus.COMPLETED)

            processing_time = time.time() - start_time
            record_job_metrics(
                "cv-worker", "completed", "cv_processing", processing_time
            )

            logger.info(
                f"Job {job_id} completed successfully in {processing_time:.2f}s"
            )

            # Schedule cleanup
            self._schedule_cleanup(job_id)

        except Exception as e:
            logger.error(f"Job {job_id} failed: {str(e)}")

            # Mark as failed (with retry)
            redis_queue.mark_job_failed(task_id, str(e), retry=True)
            await self.job_service.update_job_status(job_id, JobStatus.FAILED, str(e))

            processing_time = time.time() - start_time
            record_job_metrics("cv-worker", "failed", "cv_processing", processing_time)
            record_error_metrics("cv-worker", "ProcessingError", "process_job")

        finally:
            clear_request_context()

    def _schedule_cleanup(self, job_id: str):
        """Schedule cleanup task"""
        try:
            _ = {
                "job_id": job_id,
                "scheduled_at": asyncio.get_event_loop().time() + 300,  # 5 minutes
            }
            redis_queue.redis_client.lpush(settings.REDIS_CLEANUP_QUEUE, job_id)
            logger.debug(f"Scheduled cleanup for job {job_id}")
        except Exception as e:
            logger.error(f"Failed to schedule cleanup for job {job_id}: {str(e)}")


class CleanupWorker:
    """Redis-based cleanup worker"""

    def __init__(self):
        self.running = False

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Cleanup worker received signal {signum}, shutting down...")
        self.running = False

    async def start(self):
        """Start the cleanup worker"""
        setup_logging("cv-cleanup-worker", settings.LOG_LEVEL)
        logger.info("Starting cleanup worker")

        self.running = True

        while self.running:
            try:
                # Get cleanup job
                result = redis_queue.redis_client.brpop(
                    settings.REDIS_CLEANUP_QUEUE, timeout=30
                )
                if not result:
                    # Periodic cleanup of expired jobs
                    cleaned = redis_queue.cleanup_expired_jobs()
                    if cleaned > 0:
                        logger.info(f"Cleaned up {cleaned} expired jobs")
                    continue

                _, job_id = result
                await self._cleanup_job(job_id)

            except Exception as e:
                logger.error(f"Cleanup worker error: {str(e)}")
                await asyncio.sleep(5)

        logger.info("Cleanup worker stopped")

    async def _cleanup_job(self, job_id: str):
        """Clean up job files"""
        try:
            logger.info(f"Cleaning up job {job_id}")
            FileService.cleanup_temp_file(job_id)
            logger.debug(f"Job {job_id} cleanup completed")
        except Exception as e:
            logger.error(f"Failed to cleanup job {job_id}: {str(e)}")


async def main():
    """Main worker entry point"""
    worker_type = sys.argv[1] if len(sys.argv) > 1 else "processing"

    if worker_type == "cleanup":
        worker = CleanupWorker()
    else:
        worker = CVProcessingWorker()

    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())
