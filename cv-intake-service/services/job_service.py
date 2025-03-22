import logging
import uuid
from typing import Optional

from fastapi import BackgroundTasks, HTTPException
from fastapi.concurrency import run_in_threadpool
from models.job import JobCreate, JobUpdate, JobStatus, Job, JobResponse
from repositories.job_repository import JobRepository
from services.file_service import FileService
from services.processing_service import ProcessingService
from utils.errors import JobServiceError

logger = logging.getLogger(__name__)


class JobService:
    """Service for managing CV processing jobs"""

    def __init__(self):
        self.job_repo = JobRepository()

    async def create_job(self, file_path: str) -> Job:
        try:
            job_id = str(uuid.uuid4())
            job_create = JobCreate(file_path=file_path)

            job = await run_in_threadpool(
                lambda: self.job_repo.create(job_id, job_create)
            )

            return job
        except Exception as e:
            logger.error(f"Error creating job: {str(e)}")
            raise JobServiceError(f"Failed to create job: {str(e)}")

    async def get_job(self, job_id: str) -> Optional[Job]:
        try:
            job = await run_in_threadpool(
                lambda: self.job_repo.get(job_id)
            )

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

    async def process_job(self, job_id: str, background_tasks: BackgroundTasks):
        """Queue a job for background processing"""
        try:
            job = await self.get_job(job_id)
            if not job:
                raise JobServiceError(f"Job not found: {job_id}")

            background_tasks.add_task(self._process_job_task, job_id, job.file_path)

            return {"job_id": job_id, "status": "queued for processing"}
        except Exception as e:
            logger.error(f"Error queueing job {job_id}: {str(e)}")
            raise JobServiceError(f"Failed to queue job: {str(e)}")

    async def _process_job_task(self, job_id: str, file_path: str):
        """Background task for processing a CV"""
        try:
            # Update job status to processing
            await self.update_job(
                job_id,
                JobUpdate(status=JobStatus.PROCESSING)
            )

            result_data = await ProcessingService.process_cv(file_path)
            logger.debug(
                f"Received processing result data with keys: "
                f"{result_data.keys() if isinstance(result_data, dict) else 'not a dict'}")

            if isinstance(result_data, dict) and "structured_data" in result_data:
                storage_result = await ProcessingService.store_cv_data(job_id,
                                                                       result_data["structured_data"])
                if isinstance(storage_result, dict) and "cv_id" in storage_result:
                    cv_id = storage_result["cv_id"]
                    if "metadata" not in result_data:
                        result_data["metadata"] = {}
                    result_data["metadata"]["cv_id"] = cv_id

            # Make sure we have a result to store - empty dict is better than None
            if result_data is None:
                result_data = {}

            logger.debug(f"Updating job {job_id} to COMPLETED with result data of size "
                         f"{len(str(result_data))} bytes")

            # Update job with results
            updated_job = await self.update_job(
                job_id,
                JobUpdate(
                    status=JobStatus.COMPLETED,
                    result=result_data,
                    result_url=f"/api/v1/results/{job_id}"
                )
            )
            if not updated_job:
                raise JobServiceError(f"Failed to update job: {job_id}")

            # Check if the update was successful by verifying the result field
            logger.debug(f"Job updated - status: {updated_job.status}, "
                         f"result type: {type(updated_job.result)}")
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
                job_id,
                JobUpdate(
                    status=JobStatus.FAILED,
                    error=str(e)
                )
            )

            # Clean up temporary file on error as well
            FileService.cleanup_temp_file(job_id)

    def to_response(self, job: Job) -> JobResponse:
        """Convert Job model to JobResponse model"""
        return JobResponse(
            job_id=job.job_id,
            status=job.status,
            created_at=job.created_at,
            updated_at=job.updated_at,
            result_url=job.result_url,
            error=job.error
        )
