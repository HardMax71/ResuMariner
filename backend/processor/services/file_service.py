import logging
import os
import uuid
from pathlib import Path

import aiofiles
import aiofiles.os
from botocore.exceptions import ClientError
from django.conf import settings

from processor.utils.circuit_breaker import create_custom_circuit_breaker

s3_circuit_breaker = create_custom_circuit_breaker(
    name="s3_storage", fail_max=3, reset_timeout=45, exclude=[ValueError, FileNotFoundError]
)

logger = logging.getLogger(__name__)


class FileService:
    _temp_files: dict[str, str] = {}

    @staticmethod
    async def save_validated_content(content: bytes, filename: str, job_id: str) -> str:
        """
        Save already-validated file content to temporary and durable storage.

        Args:
            content: Validated file content as bytes
            filename: Original filename (for extension extraction)
            job_id: Unique job identifier

        Returns:
            Path to the saved temporary file
        """
        file_ext = os.path.splitext(filename)[1].lower()

        Path(settings.TEMP_DIR).mkdir(parents=True, exist_ok=True)
        temp_filename = f"{job_id}{file_ext}"
        temp_path = os.path.join(settings.TEMP_DIR, temp_filename)

        async with aiofiles.open(temp_path, "wb") as f:
            await f.write(content)

        FileService._temp_files[job_id] = temp_path
        await FileService._handle_durable_storage(temp_path, job_id, file_ext)

        return temp_path

    @staticmethod
    async def _handle_durable_storage(temp_path: str, job_id: str, file_ext: str) -> None:
        """
        Handle saving to durable storage (S3 or local).

        Args:
            temp_path: Path to temporary file
            job_id: Unique job identifier
            file_ext: File extension including dot
        """
        if settings.DURABLE_STORAGE == "s3":
            await FileService._save_to_s3_async(temp_path, job_id, file_ext)
        elif settings.DURABLE_STORAGE == "local":
            Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
            temp_filename = f"{job_id}{file_ext}"
            durable_path = os.path.join(settings.UPLOAD_DIR, temp_filename)
            # For async file copy
            async with aiofiles.open(temp_path, "rb") as src:
                async with aiofiles.open(durable_path, "wb") as dst:
                    await dst.write(await src.read())

    @staticmethod
    async def cleanup_temp_file(job_id: str) -> None:
        try:
            if job_id in FileService._temp_files:
                temp_path = FileService._temp_files[job_id]
                if await aiofiles.os.path.exists(temp_path):
                    await aiofiles.os.remove(temp_path)
                del FileService._temp_files[job_id]
        except Exception:
            logger.warning("Error cleaning up temp file for job %s", job_id)

    @staticmethod
    async def cleanup_all_job_files(job_id: str, file_ext: str | None = None) -> None:
        await FileService.cleanup_temp_file(job_id)

        if settings.DURABLE_STORAGE == "s3":
            await FileService.delete_from_s3_async(job_id, file_ext)
        elif settings.DURABLE_STORAGE == "local":
            await FileService.cleanup_local_file(job_id, file_ext)

    @staticmethod
    async def cleanup_local_file(job_id: str, file_ext: str | None = None) -> None:
        if not file_ext:
            pattern = os.path.join(settings.UPLOAD_DIR, f"{job_id}.*")
            import glob

            files = glob.glob(pattern)
            for file_path in files:
                try:
                    await aiofiles.os.remove(file_path)
                except Exception:
                    logger.warning("Error removing local file %s", file_path)
        else:
            file_path = os.path.join(settings.UPLOAD_DIR, f"{job_id}{file_ext}")
            if await aiofiles.os.path.exists(file_path):
                try:
                    await aiofiles.os.remove(file_path)
                except Exception:
                    logger.warning("Error removing local file %s", file_path)

    @staticmethod
    async def delete_from_s3_async(job_id: str, file_ext: str | None = None) -> None:
        import aioboto3

        session = aioboto3.Session()
        async with session.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL if settings.AWS_S3_ENDPOINT_URL else None,
        ) as s3:
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME

            if file_ext:
                key = f"{job_id}{file_ext}"
                try:
                    await s3.delete_object(Bucket=bucket_name, Key=key)
                    logger.info("Deleted S3 object %s from bucket %s", key, bucket_name)
                except ClientError as e:
                    if e.response["Error"]["Code"] != "404":
                        logger.warning("Error deleting S3 object %s: %s", key, e)
            else:
                try:
                    response = await s3.list_objects_v2(Bucket=bucket_name, Prefix=job_id)
                    if "Contents" in response:
                        objects = [{"Key": obj["Key"]} for obj in response["Contents"]]
                        if objects:
                            await s3.delete_objects(Bucket=bucket_name, Delete={"Objects": objects})
                            logger.info("Deleted %d S3 objects with prefix %s", len(objects), job_id)
                except ClientError as e:
                    logger.warning("Error deleting S3 objects with prefix %s: %s", job_id, e)

    @staticmethod
    async def download_from_s3_async(s3_key: str) -> str:
        temp_path = os.path.join(settings.TEMP_DIR, f"s3_{uuid.uuid4()}_{os.path.basename(s3_key)}")
        Path(os.path.dirname(temp_path)).mkdir(parents=True, exist_ok=True)

        import aioboto3

        session = aioboto3.Session()
        async with session.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL if settings.AWS_S3_ENDPOINT_URL else None,
        ) as s3:
            await s3.download_file(settings.AWS_STORAGE_BUCKET_NAME, s3_key, temp_path)
        return temp_path

    @staticmethod
    async def _save_to_s3_async(file_path: str, job_id: str, file_ext: str) -> str:
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        key = f"{job_id}{file_ext}"

        import aioboto3

        session = aioboto3.Session()
        async with session.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        ) as s3:
            try:
                await s3.head_bucket(Bucket=bucket_name)
            except ClientError as e:
                code = e.response.get("Error", {}).get("Code")
                if code == "404":
                    await s3.create_bucket(Bucket=bucket_name)
                else:
                    raise
            await s3.upload_file(file_path, bucket_name, key)
        logger.info("Uploaded file to S3: %s", key)
        return key
