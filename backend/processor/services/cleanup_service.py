from datetime import datetime, timedelta
from pathlib import Path

from storage.services.graph_db_service import GraphDBService
from storage.services.vector_db_service import VectorDBService

from ..serializers import JobStatus
from ..services.file_service import FileService
from ..services.job_service import JobService


class CleanupService:
    def __init__(self) -> None:
        self.job_service = JobService()

    async def cleanup_job(self, job_id: str) -> bool:
        job = await self.job_service.get_job(job_id)
        if not job:
            return False

        if job.file_path:
            file_ext = Path(job.file_path).suffix
        else:
            file_ext = None

        graph_db = await GraphDBService.get_instance()
        vector_db = await VectorDBService.get_instance()

        await FileService.cleanup_all_job_files(job_id, file_ext)
        await graph_db.delete_resume(resume_id=job_id)
        await vector_db.delete_resume_vectors(job_id)
        return await self.job_service.delete_job(job_id)

    async def cleanup_old_jobs(self, days: int, force: bool = False) -> int:
        deleted_count = 0
        jobs = await self.job_service.list_jobs(limit=1000)
        cutoff_date = datetime.now() - timedelta(days=days)

        for job in jobs:
            if job.created_at < cutoff_date:
                if force or job.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                    cleaned = await self.cleanup_job(job.job_id)
                    if cleaned:
                        deleted_count += 1

        return deleted_count
