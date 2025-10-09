from datetime import datetime, timedelta
from pathlib import Path

from ..serializers import JobStatus
from ..services.file_service import FileService
from ..services.job_service import JobService


class CleanupService:
    def __init__(self) -> None:
        self.job_service = JobService()

    async def cleanup_job(self, uid: str, graph_db, vector_db) -> bool:
        job = await self.job_service.get_job(uid)
        if not job:
            return False

        file_ext = Path(job.file_path).suffix if job.file_path else None

        await FileService.cleanup_all_job_files(uid, file_ext)
        await graph_db.delete_resume(job.uid)
        await vector_db.delete_resume_vectors(job.uid)
        return await self.job_service.delete_job(uid)

    async def cleanup_old_jobs(self, days: int, graph_db, vector_db, force: bool = False) -> int:
        deleted_count = 0
        jobs = await self.job_service.list_jobs(limit=1000)
        cutoff_date = datetime.now() - timedelta(days=days)

        for job in jobs:
            if job.created_at < cutoff_date:
                if force or job.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                    cleaned = await self.cleanup_job(job.uid, graph_db, vector_db)
                    if cleaned:
                        deleted_count += 1

        return deleted_count
