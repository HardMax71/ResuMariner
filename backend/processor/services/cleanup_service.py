from ..services.file_service import FileService
from ..services.job_service import JobService


class CleanupService:
    def __init__(self) -> None:
        self.job_service = JobService()

    async def cleanup_job(self, uid: str, graph_db, vector_db) -> bool:
        job = await self.job_service.get_job(uid)
        if not job:
            return False

        await FileService.cleanup_all_job_files(uid)
        await graph_db.delete_resume(job.uid)
        await vector_db.delete_resume_vectors(job.uid)
        return await self.job_service.delete_job(uid)
