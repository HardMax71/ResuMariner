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
        self.sleep_interval = 60.0
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        self.job_service = JobService()
        self.cleanup_service = CleanupService()
        self.redis_queue = RedisJobQueue()
        self.cleanup_batch_size = 50
        self.retention_days = settings.JOB_RETENTION_DAYS

    async def process_iteration(self) -> bool:
        tasks_processed = await self._process_scheduled_cleanups()
        old_jobs_cleaned = await self._cleanup_old_jobs()
        orphaned_files_cleaned = await self._cleanup_orphaned_files()

        return tasks_processed or old_jobs_cleaned > 0 or orphaned_files_cleaned > 0

    async def _process_scheduled_cleanups(self) -> bool:
        cleanup_tasks = self.redis_queue.get_cleanup_tasks()

        if not cleanup_tasks:
            return False

        current_time = time.time()
        cleaned = False

        for task in cleanup_tasks[: self.cleanup_batch_size]:
            job_id = task.job_id
            cleanup_time = task.cleanup_time

            if job_id and current_time >= cleanup_time:
                await self._cleanup_job(job_id)
                self.redis_queue.remove_cleanup_task(job_id)
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

            FileService.cleanup_all_job_files(job_id, file_ext)
            success = await self.cleanup_service.cleanup_job(job_id)
            if success:
                self.logger.info("Successfully cleaned up job %s", job_id)
            else:
                self.logger.warning("Failed to cleanup job %s", job_id)

        except Exception as e:
            self.logger.error("Failed to cleanup job %s: %s", job_id, e)

    async def startup(self):
        """No async initialization needed."""
        pass

    async def shutdown(self):
        """No cleanup needed."""
        pass
