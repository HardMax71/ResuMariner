import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import aioboto3
import aiofiles
import aiofiles.os
from botocore.exceptions import ClientError
from django.conf import settings
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)


@dataclass
class FileInfo:
    path: str
    name: str
    ext: str
    source: str  # "s3" or "local"


class FileService:
    """File operations for resume processing including S3 integration and validation."""

    @staticmethod
    async def prepare_for_processing(file_path: str) -> FileInfo:
        """
        Prepare file for processing - handle S3 download, validation, and info extraction.

        Args:
            file_path: Local path or s3://key format

        Returns:
            FileInfo with actual path, name, extension, and source
        """
        if file_path.startswith("s3://"):
            s3_key = file_path[5:]  # Remove s3:// prefix
            actual_path = await FileService.download_from_s3_async(s3_key)
            source = "s3"
        else:
            actual_path = file_path
            source = "local"

        if not os.path.isfile(actual_path):
            raise FileNotFoundError(f"File not found: {actual_path}")

        path_obj = Path(actual_path)
        if not path_obj.name:
            logger.error("File preparation failed: file name is missing for path %s", actual_path)
            raise ValidationError("File name is missing")

        if not path_obj.suffix:
            logger.error("File preparation failed: missing extension for file %s", path_obj.name)
            raise ValidationError("Invalid file name or missing extension")

        return FileInfo(path=actual_path, name=path_obj.name, ext=path_obj.suffix.lower(), source=source)

    @staticmethod
    @asynccontextmanager
    async def _s3_client() -> AsyncIterator[Any]:
        """Context manager for S3 client with consistent config."""
        session = aioboto3.Session()
        async with session.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL or None,
        ) as s3:
            yield s3

    @staticmethod
    async def save_validated_content(content: bytes, filename: str, uid: str) -> str:
        """
        Save already-validated file content to temporary and durable storage.

        Args:
            content: Validated file content as bytes
            filename: Original filename (for extension extraction)
            uid: Unique identifier

        Returns:
            Path to the saved temporary file
        """
        file_ext = os.path.splitext(filename)[1].lower()

        await aiofiles.os.makedirs(settings.TEMP_DIR, exist_ok=True)
        temp_filename = f"{uid}{file_ext}"
        temp_path = os.path.join(settings.TEMP_DIR, temp_filename)

        async with aiofiles.open(temp_path, "wb") as f:
            await f.write(content)

        await FileService._handle_durable_storage(temp_path, uid, file_ext)

        return temp_path

    @staticmethod
    async def _handle_durable_storage(temp_path: str, uid: str, file_ext: str) -> None:
        """
        Handle saving to durable storage (S3 or local).

        Args:
            temp_path: Path to temporary file
            uid: Unique identifier
            file_ext: File extension including dot
        """
        if settings.DURABLE_STORAGE == "s3":
            await FileService._save_to_s3_async(temp_path, uid, file_ext)
        elif settings.DURABLE_STORAGE == "local":
            await aiofiles.os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            temp_filename = f"{uid}{file_ext}"
            durable_path = os.path.join(settings.UPLOAD_DIR, temp_filename)
            async with aiofiles.open(temp_path, "rb") as src:
                async with aiofiles.open(durable_path, "wb") as dst:
                    await dst.write(await src.read())

    @staticmethod
    async def cleanup_all_job_files(uid: str) -> None:
        # Cleanup temp files - just find any file with this uid
        temp_dir = Path(settings.TEMP_DIR)
        for temp_file in temp_dir.glob(f"{uid}.*"):
            try:
                await aiofiles.os.remove(temp_file)
            except OSError as e:
                logger.warning("Failed to cleanup temp file %s: %s", temp_file, e)

        # Cleanup durable storage
        if settings.DURABLE_STORAGE == "s3":
            await FileService.delete_from_s3_async(uid)
        elif settings.DURABLE_STORAGE == "local":
            await FileService.cleanup_local_file(uid)

    @staticmethod
    async def cleanup_local_file(uid: str) -> None:
        upload_dir = Path(settings.UPLOAD_DIR)
        for file_path in upload_dir.glob(f"{uid}.*"):
            try:
                await aiofiles.os.remove(file_path)
            except OSError as e:
                logger.warning("Failed to cleanup local file %s: %s", file_path, e)

    @staticmethod
    async def delete_from_s3_async(uid: str) -> None:
        async with FileService._s3_client() as s3:
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            try:
                response = await s3.list_objects_v2(Bucket=bucket_name, Prefix=uid)
                if "Contents" in response:
                    objects = [{"Key": obj["Key"]} for obj in response["Contents"]]
                    if objects:
                        await s3.delete_objects(Bucket=bucket_name, Delete={"Objects": objects})
                        logger.info("Deleted %d S3 objects with prefix %s", len(objects), uid)
            except ClientError as e:
                logger.warning("Error deleting S3 objects with prefix %s: %s", uid, e)

    @staticmethod
    async def download_from_s3_async(s3_key: str) -> str:
        temp_path = os.path.join(settings.TEMP_DIR, os.path.basename(s3_key))
        await aiofiles.os.makedirs(settings.TEMP_DIR, exist_ok=True)

        async with FileService._s3_client() as s3:
            await s3.download_file(settings.AWS_STORAGE_BUCKET_NAME, s3_key, temp_path)
        return temp_path

    @staticmethod
    async def _save_to_s3_async(file_path: str, uid: str, file_ext: str) -> str:
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        key = f"{uid}{file_ext}"

        async with FileService._s3_client() as s3:
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
