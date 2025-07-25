import logging
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import BackgroundTasks, HTTPException
from fastapi.concurrency import run_in_threadpool
from models.job import JobCreate, JobUpdate, JobStatus, Job, JobResponse
from repositories.job_repository import JobRepository
from services.file_service import FileService
from services.processing_service import ProcessingService
from utils.errors import JobServiceError
from utils.monitoring import trace_function, record_job_metrics, record_error_metrics
from config import settings

logger = logging.getLogger(__name__)


class JobService:
    """Service for managing CV processing jobs"""

    def __init__(self):
        self.job_repo = JobRepository()
        self.retention_days = settings.JOB_RETENTION_DAYS

    @trace_function("job_service.create_job")
    async def create_job(self, file_path: str) -> Job:
        try:
            job_id = str(uuid.uuid4())
            job_create = JobCreate(file_path=file_path)

            job = await run_in_threadpool(
                lambda: self.job_repo.create(job_id, job_create)
            )

            record_job_metrics("cv-intake-service", "created", "cv_processing")
            return job
        except Exception as e:
            logger.error(f"Error creating job: {str(e)}")
            record_error_metrics("cv-intake-service", "JobServiceError", "create_job")
            raise JobServiceError(f"Failed to create job: {str(e)}")

    async def get_job(self, job_id: str) -> Optional[Job]:
        try:
            job = await run_in_threadpool(lambda: self.job_repo.get(job_id))

            if not job:
                raise HTTPException(status_code=404, detail="Job not found")

            return job
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting job {job_id}: {str(e)}")
            raise JobServiceError(f"Failed to get job: {str(e)}")

    async def update_job(self, job_id: str, job_update: JobUpdate) -> Optional[Job]:
        """Update a job"""
        try:
            job = await run_in_threadpool(
                lambda: self.job_repo.update(job_id, job_update)
            )

            if not job:
                raise HTTPException(status_code=404, detail="Job not found")

            return job
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating job {job_id}: {str(e)}")
            raise JobServiceError(f"Failed to update job: {str(e)}")

    @trace_function("job_service.process_job")
    async def process_job(self, job_id: str, background_tasks: BackgroundTasks):
        """Queue a job for processing"""
        try:
            job = await self.get_job(job_id)
            if not job:
                raise JobServiceError(f"Job not found: {job_id}")

            if settings.ENABLE_ASYNC_PROCESSING:
                # Use Redis queue for async processing
                from utils.redis_queue import redis_queue

                task_id = redis_queue.enqueue_job(job_id, job.file_path)

                # Update job with task ID
                await self.update_job(
                    job_id,
                    JobUpdate(status=JobStatus.PROCESSING, result={"task_id": task_id}),
                )

                record_job_metrics("cv-intake-service", "queued", "cv_processing")
                logger.info(
                    f"Job {job_id} queued for async processing with task {task_id}"
                )
                return {
                    "job_id": job_id,
                    "status": "queued for async processing",
                    "task_id": task_id,
                }
            else:
                # Fallback to background task
                background_tasks.add_task(self._process_job_task, job_id, job.file_path)
                record_job_metrics("cv-intake-service", "queued", "cv_processing")
                logger.info(f"Job {job_id} queued for background processing")
                return {"job_id": job_id, "status": "queued for processing"}

        except Exception as e:
            logger.error(f"Error queueing job {job_id}: {str(e)}")
            record_error_metrics("cv-intake-service", "JobServiceError", "process_job")
            raise JobServiceError(f"Failed to queue job: {str(e)}")

    async def _process_job_task(self, job_id: str, file_path: str):
        """Background task for processing a CV"""
        try:
            # Update job status to processing
            await self.update_job(job_id, JobUpdate(status=JobStatus.PROCESSING))

            result_data = await ProcessingService.process_cv(file_path)
            logger.debug(
                f"Received processing result data with keys: "
                f"{result_data.keys() if isinstance(result_data, dict) else 'not a dict'}"
            )

            if isinstance(result_data, dict) and "structured_data" in result_data:
                storage_result = await ProcessingService.store_cv_data(
                    job_id, result_data["structured_data"]
                )
                if isinstance(storage_result, dict) and "cv_id" in storage_result:
                    cv_id = storage_result["cv_id"]
                    if "metadata" not in result_data:
                        result_data["metadata"] = {}
                    result_data["metadata"]["cv_id"] = cv_id

            # Make sure we have a result to store - empty dict is better than None
            if result_data is None:
                result_data = {}

            logger.debug(
                f"Updating job {job_id} to COMPLETED with result data of size "
                f"{len(str(result_data))} bytes"
            )

            # Update job with results
            updated_job = await self.update_job(
                job_id,
                JobUpdate(
                    status=JobStatus.COMPLETED,
                    result=result_data,
                    result_url=f"/api/v1/results/{job_id}",
                ),
            )
            if not updated_job:
                raise JobServiceError(f"Failed to update job: {job_id}")

            # Check if the update was successful by verifying the result field
            logger.debug(
                f"Job updated - status: {updated_job.status}, "
                f"result type: {type(updated_job.result)}"
            )
            if isinstance(updated_job.result, dict):
                logger.debug(f"Result keys after update: {updated_job.result.keys()}")

            logger.info(f"Job {job_id} completed successfully")

            # Clean up temporary file now that processing is complete
            FileService.cleanup_temp_file(job_id)

        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}")
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")

            await self.update_job(
                job_id, JobUpdate(status=JobStatus.FAILED, error=str(e))
            )

            # Clean up temporary file on error as well
            FileService.cleanup_temp_file(job_id)

    async def get_expired_jobs(self, cutoff_date: datetime) -> List[Job]:
        """Get jobs older than cutoff date"""
        try:
            return await run_in_threadpool(
                lambda: self.job_repo.get_expired_jobs(cutoff_date)
            )
        except Exception as e:
            logger.error(f"Failed to get expired jobs: {str(e)}")
            raise JobServiceError(f"Failed to get expired jobs: {str(e)}")

    async def delete_job(self, job_id: str) -> bool:
        """Delete a job"""
        try:
            return await run_in_threadpool(lambda: self.job_repo.delete(job_id))
        except Exception as e:
            logger.error(f"Failed to delete job {job_id}: {str(e)}")
            raise JobServiceError(f"Failed to delete job: {str(e)}")

    async def update_job_result(self, job_id: str, result: Dict[str, Any]) -> bool:
        """Update job result"""
        try:
            await self.update_job(job_id, JobUpdate(result=result))
            return True
        except Exception as e:
            logger.error(f"Failed to update job result {job_id}: {str(e)}")
            raise JobServiceError(f"Failed to update job result: {str(e)}")

    async def update_job_status(
        self, job_id: str, status: JobStatus, error: str = None
    ) -> bool:
        """Update job status"""
        try:
            update_data = JobUpdate(status=status)
            if error:
                update_data.error = error
            await self.update_job(job_id, update_data)
            return True
        except Exception as e:
            logger.error(f"Failed to update job status {job_id}: {str(e)}")
            raise JobServiceError(f"Failed to update job status: {str(e)}")

    def to_response(self, job: Job) -> JobResponse:
        """Convert Job model to JobResponse model"""
        return JobResponse(
            job_id=job.job_id,
            status=job.status,
            created_at=job.created_at,
            updated_at=job.updated_at,
            result_url=job.result_url,
            error=job.error,
        )
