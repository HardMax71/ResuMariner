import logging
import os
import shutil
import uuid
from typing import Tuple, Dict, Optional

from config import settings
from fastapi import UploadFile, HTTPException
from utils.errors import FileServiceError

logger = logging.getLogger(__name__)


class FileService:
    """Service for managing file uploads and storage"""

    # In-memory tracking of temporary files for cleanup
    _temp_files: Dict[str, str] = {}

    @staticmethod
    async def save_uploaded_file(file: UploadFile, job_id: str) -> str:
        """
        Save an uploaded file to a temporary location and optionally to durable storage.
        Returns a file path that can be used for processing.
        """
        try:
            # Validate file type
            if not file or not file.filename:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} was not found.",
                )
            is_valid, file_ext = FileService.validate_file_type(file.filename)
            if not is_valid:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type. Allowed extensions: {', '.join(settings.ALLOWED_FILE_EXTENSIONS)}"
                )

            # Ensure temp directory exists
            os.makedirs(settings.TEMP_DIR, exist_ok=True)

            # Create a unique filename for temp storage
            temp_filename = f"{job_id}{file_ext}"
            temp_path = os.path.join(settings.TEMP_DIR, temp_filename)

            # Save to temp file
            await file.seek(0)
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            logger.debug(f"File saved to temporary location: {temp_path}")

            # Track this temp file for later cleanup
            FileService._temp_files[job_id] = temp_path

            # If durable storage is enabled, save a copy
            if settings.DURABLE_STORAGE == "s3":
                s3_key = await FileService._save_to_s3(temp_path, job_id, file_ext)
                logger.info(f"File durably stored in S3 with key: {s3_key}")
                return temp_path  # Still return temp path for processing

            elif settings.DURABLE_STORAGE == "local":
                # Create the uploads directory if it doesn't exist
                os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

                # Copy from temp to durable location
                durable_path = os.path.join(settings.UPLOAD_DIR, temp_filename)
                shutil.copy2(temp_path, durable_path)

                logger.info(f"File durably stored locally at: {durable_path}")
                return temp_path  # Still return temp path for processing

            # If no durable storage, just return the temp path
            return temp_path

        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            if isinstance(e, HTTPException):
                raise e
            raise FileServiceError(f"Failed to save file: {str(e)}")

    @staticmethod
    async def _save_to_s3(file_path: str, job_id: str, file_ext: str) -> str:
        """Upload a file to S3 and return the S3 key"""
        try:
            import boto3
            from botocore.exceptions import ClientError

            # Initialize S3 client
            s3 = boto3.client('s3',
                              aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                              region_name=settings.S3_REGION,
                              endpoint_url=settings.S3_ENDPOINT_URL if settings.S3_ENDPOINT_URL else None
                              )

            # Check if bucket exists
            bucket_name = settings.S3_BUCKET_NAME
            try:
                s3.head_bucket(Bucket=bucket_name)
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code')
                if error_code == '404':
                    logger.info(f"Bucket {bucket_name} doesn't exist, creating...")
                    s3.create_bucket(Bucket=bucket_name)
                else:
                    logger.error(f"Error checking S3 bucket: {str(e)}")
                    raise FileServiceError(f"Failed to access S3 bucket: {str(e)}")

            # Upload file to S3
            key = f"{job_id}{file_ext}"
            s3.upload_file(file_path, bucket_name, key)

            return key

        except ImportError:
            logger.error("boto3 not installed. Please install boto3 to use S3 storage")
            raise FileServiceError("boto3 not installed. Please install boto3 to use S3 storage")
        except Exception as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            raise FileServiceError(f"Failed to upload file to S3: {str(e)}")

    @staticmethod
    def validate_file_type(filename: str) -> Tuple[bool, str]:
        """Validate that the file has an allowed extension"""
        file_ext = os.path.splitext(filename)[1].lower()
        is_valid = file_ext in settings.ALLOWED_FILE_EXTENSIONS
        return is_valid, file_ext

    @staticmethod
    def get_durable_file_path(job_id: str, file_ext: str | None = None) -> Optional[str]:
        """
        Get the path to a durably stored file if it exists.
        This is used when retrieving files after processing.
        """
        if settings.DURABLE_STORAGE == "local":
            # If we don't know the extension, try to find a matching file
            if file_ext is None:
                for ext in settings.ALLOWED_FILE_EXTENSIONS:
                    path = os.path.join(settings.UPLOAD_DIR, f"{job_id}{ext}")
                    if os.path.exists(path):
                        return path
                return None

            # If we know the extension, check if the file exists
            path = os.path.join(settings.UPLOAD_DIR, f"{job_id}{file_ext}")
            return path if os.path.exists(path) else None

        elif settings.DURABLE_STORAGE == "s3":
            # For S3, we need to know the extension
            if file_ext is None:
                logger.warning(f"Cannot get S3 file path without knowing the extension for job {job_id}")
                return None

            # Return a marker for S3 files
            return f"s3:{job_id}{file_ext}"

        else:
            # No durable storage
            return None

    @staticmethod
    def cleanup_temp_file(job_id: str) -> None:
        """
        Clean up the temporary file for a job.
        This should be called after processing is complete.
        """
        try:
            # Check if we have a record of this temp file
            if job_id in FileService._temp_files:
                temp_path = FileService._temp_files[job_id]

                # Remove the file if it exists
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    logger.debug(f"Temporary file removed: {temp_path}")

                # Remove from tracking
                del FileService._temp_files[job_id]
        except Exception as e:
            logger.warning(f"Error cleaning up temporary file for job {job_id}: {str(e)}")

    @staticmethod
    def download_from_s3(s3_key: str) -> str:
        """
        Download a file from S3 to a temporary location and return the path.
        This is used for retrieving files from S3 for processing or download.
        """
        try:
            import boto3

            # Create a temporary file path
            temp_path = os.path.join(settings.TEMP_DIR, f"s3_{uuid.uuid4()}_{os.path.basename(s3_key)}")
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)

            # Download from S3
            s3 = boto3.client('s3',
                              aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                              region_name=settings.S3_REGION,
                              endpoint_url=settings.S3_ENDPOINT_URL if settings.S3_ENDPOINT_URL else None
                              )

            s3.download_file(settings.S3_BUCKET_NAME, s3_key, temp_path)
            logger.debug(f"Downloaded S3 file {s3_key} to {temp_path}")

            return temp_path

        except Exception as e:
            logger.error(f"Error downloading from S3: {str(e)}")
            raise FileServiceError(f"Failed to download file from S3: {str(e)}")
