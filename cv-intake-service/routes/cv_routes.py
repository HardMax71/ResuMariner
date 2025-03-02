import logging
import uuid

from fastapi import APIRouter, File, UploadFile, BackgroundTasks, HTTPException
from models.job import JobResponse, JobStatus
from services.file_service import FileService
from services.job_service import JobService

router = APIRouter()
job_service = JobService()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=JobResponse)
async def upload_cv_for_processing(background_tasks: BackgroundTasks,
                                   file: UploadFile = File(...)):
    try:
        is_valid, file_ext = FileService.validate_file_type(file.filename)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")
        if not file_ext:
            raise HTTPException(status_code=400, detail="File extension is missing")

        job_id = str(uuid.uuid4())
        file_path = await FileService.save_uploaded_file(file, job_id)
        job = await job_service.create_job(file_path)

        await job_service.process_job(job.job_id, background_tasks)
        return job_service.to_response(job)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process upload: {str(e)}")


@router.get("/status/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    try:
        job = await job_service.get_job(job_id)
        return job_service.to_response(job)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")


@router.get("/results/{job_id}")
async def get_job_results(job_id: str):
    try:
        job = await job_service.get_job(job_id)

        logger.info(f"Job {job_id}: status={job.status}, result type={type(job.result)}")
        if hasattr(job.result, 'keys'):
            logger.info(f"Result keys: {job.result.keys() if job.result else 'None'}")

        if job.status != JobStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"Job is not completed. Current status: {job.status}"
            )

        # Return empty dict if result is None or empty
        if job.result is None:
            logger.warning(f"Job {job_id} has None result, returning empty dict")
            return {}

        # Make sure job.result is a dictionary before returning
        if not isinstance(job.result, dict):
            logger.info(f"Job {job_id} result is not a dictionary, type: {type(job.result)}")
            # Try to convert to dict if it's a string
            if isinstance(job.result, str) and job.result.strip():
                import json
                try:
                    return json.loads(job.result)
                except json.JSONDecodeError:
                    # If parsing fails, return as data field
                    return {"data": job.result}
            return {"data": job.result}

        # Return the result
        logger.info(f"Successfully returning result for job {job_id}")
        return job.result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job results for {job_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get job results: {str(e)}")
