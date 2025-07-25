import logging
import uuid

from fastapi import (
    APIRouter,
    File,
    UploadFile,
    BackgroundTasks,
    HTTPException,
    Depends,
    Request,
)
from pydantic import ValidationError
from models.job import JobResponse, JobStatus, FileUpload
from services.file_service import FileService
from services.job_service import JobService
from utils.security import validate_api_key, limiter

router = APIRouter()
job_service = JobService()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=JobResponse)
@limiter.limit("5/minute")
async def upload_cv_for_processing(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    api_key: str = Depends(validate_api_key),
):
    if not file or not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided",
        )
    try:
        # Read file content for validation
        content = await file.read()
        await file.seek(0)  # Reset file pointer

        # Validate using Pydantic model
        try:
            FileUpload.from_upload_file(file, content)
        except ValidationError as e:
            error_msg = "; ".join(
                [
                    f"{'.'.join(str(x) for x in error['loc'])}: {error['msg']}"
                    for error in e.errors()
                ]
            )
            raise HTTPException(
                status_code=400, detail=f"File validation failed: {error_msg}"
            )

        job_id = str(uuid.uuid4())
        file_path = await FileService.save_uploaded_file(file, job_id)
        job = await job_service.create_job(file_path)

        await job_service.process_job(job.job_id, background_tasks)
        return job_service.to_response(job)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process upload: {str(e)}"
        )


@router.get("/status/{job_id}", response_model=JobResponse)
@limiter.limit("30/minute")
async def get_job_status(
    request: Request, job_id: str, api_key: str = Depends(validate_api_key)
):
    try:
        job = await job_service.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        return job_service.to_response(job)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get job status: {str(e)}"
        )


@router.get("/results/{job_id}")
@limiter.limit("20/minute")
async def get_job_results(
    request: Request, job_id: str, api_key: str = Depends(validate_api_key)
):
    try:
        job = await job_service.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        logger.info(
            f"Job {job_id}: status={job.status}, result type={type(job.result)}"
        )
        if hasattr(job.result, "keys"):
            logger.info(f"Result keys: {job.result.keys() if job.result else 'None'}")

        if job.status != JobStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"Job is not completed. Current status: {job.status}",
            )

        # Return empty dict if result is None or empty
        if job.result is None:
            logger.warning(f"Job {job_id} has None result, returning empty dict")
            return {}

        # Make sure job.result is a dictionary before returning
        if not isinstance(job.result, dict):
            logger.info(
                f"Job {job_id} result is not a dictionary, type: {type(job.result)}"
            )
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
        raise HTTPException(
            status_code=500, detail=f"Failed to get job results: {str(e)}"
        )
