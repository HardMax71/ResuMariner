import asyncio
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path

from django.conf import settings

from ..serializers import JobStatus
from ..services.cleanup_service import CleanupService
from ..services.file_service import FileService
from ..services.job_service import JobService
from ..utils.redis_queue import RedisJobQueue
from .base import BaseWorker


class CleanupWorker(BaseWorker):
    def __init__(self):
        super().__init__()
        self.name = "cleanup"
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        self.job_service = JobService()
        self.cleanup_service = CleanupService()
        self.redis_queue = RedisJobQueue()
        self.cleanup_batch_size = 50
        self.retention_days = settings.JOB_RETENTION_DAYS
        self.cleanup_interval = 60  # Run cleanup every minute

    async def create_tasks(self) -> list[asyncio.Task]:
        """Create cleanup tasks that run periodically"""
        return [
            asyncio.create_task(self.scheduled_cleanup_processor()),
            asyncio.create_task(self.periodic_cleanup()),
        ]

    async def scheduled_cleanup_processor(self):
        """Process scheduled cleanup tasks continuously"""
        self.logger.info("Starting scheduled cleanup processor")

        while self.running:
            try:
                await self._process_scheduled_cleanups()
                await asyncio.sleep(10)  # Check every 10 seconds
            except Exception as e:
                self.logger.error(f"Scheduled cleanup error: {e}")
                await asyncio.sleep(30)

    async def periodic_cleanup(self):
        """Run periodic cleanup tasks"""
        self.logger.info("Starting periodic cleanup processor")

        while self.running:
            try:
                await self._cleanup_old_jobs()
                await self._cleanup_orphaned_files()
                await asyncio.sleep(self.cleanup_interval)
            except Exception as e:
                self.logger.error(f"Periodic cleanup error: {e}")
                await asyncio.sleep(60)

    async def _process_scheduled_cleanups(self) -> bool:
        cleanup_tasks = await self.redis_queue.get_cleanup_tasks()

        if not cleanup_tasks:
            return False

        current_time = time.time()
        cleaned = False

        for task in cleanup_tasks[: self.cleanup_batch_size]:
            job_id = task.job_id
            cleanup_time = task.cleanup_time

            if job_id and current_time >= cleanup_time:
                await self._cleanup_job(job_id)
                await self.redis_queue.remove_cleanup_task(job_id)
                cleaned = True

        return cleaned

    async def _cleanup_old_jobs(self) -> int:
        try:
            deleted = await self.cleanup_service.cleanup_old_jobs(self.retention_days, force=False)
            if deleted > 0:
                self.logger.info("Cleaned up %d old jobs", deleted)
            return deleted
        except Exception as e:
            self.logger.error("Error cleaning old jobs: %s", e)
            return 0

    async def _cleanup_orphaned_files(self) -> int:
        cleaned_count = 0

        try:
            if settings.DURABLE_STORAGE == "local" and Path(settings.UPLOAD_DIR).exists():
                upload_dir = Path(settings.UPLOAD_DIR)
                cutoff_time = datetime.now() - timedelta(days=self.retention_days)

                jobs = await self.job_service.list_jobs(limit=1000)
                active_job_ids = {job.job_id for job in jobs}

                for file_path in upload_dir.glob("*"):
                    if file_path.is_file():
                        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_mtime < cutoff_time:
                            job_id = file_path.stem
                            if job_id not in active_job_ids:
                                try:
                                    file_path.unlink()
                                    cleaned_count += 1
                                except Exception as e:
                                    self.logger.warning("Failed to delete orphaned file %s: %s", file_path, e)

            temp_dir = Path(settings.TEMP_DIR)
            if temp_dir.exists():
                cutoff_time = datetime.now() - timedelta(hours=24)
                for temp_file in temp_dir.glob("*"):
                    if temp_file.is_file():
                        file_mtime = datetime.fromtimestamp(temp_file.stat().st_mtime)
                        if file_mtime < cutoff_time:
                            try:
                                temp_file.unlink()
                                cleaned_count += 1
                            except Exception as e:
                                self.logger.warning("Failed to delete old temp file %s: %s", temp_file, e)

            if cleaned_count > 0:
                self.logger.info("Cleaned up %d orphaned files", cleaned_count)

        except Exception as e:
            self.logger.error("Error cleaning orphaned files: %s", e)

        return cleaned_count

    async def _cleanup_job(self, job_id: str) -> None:
        try:
            self.logger.info("Cleaning up job %s", job_id)

            job = await self.job_service.get_job(job_id)
            if not job:
                self.logger.warning("Job %s not found for cleanup", job_id)
                return

            if job.status not in [JobStatus.COMPLETED, JobStatus.FAILED]:
                self.logger.info("Job %s still processing, skipping cleanup", job_id)
                return

            file_ext = None
            if job.file_path:
                file_ext = Path(job.file_path).suffix

            await FileService.cleanup_all_job_files(job_id, file_ext)
            success = await self.cleanup_service.cleanup_job(job_id)
            if success:
                self.logger.info("Successfully cleaned up job %s", job_id)
            else:
                self.logger.warning("Failed to cleanup job %s", job_id)

        except Exception as e:
            self.logger.error("Failed to cleanup job %s: %s", job_id, e)

    async def startup(self):
        """Initialize connections"""
        self.logger.info("Cleanup worker initialized")

    async def shutdown(self):
        """Clean shutdown"""
        self.running = False
        self.logger.info("Cleanup worker shutdown complete")
