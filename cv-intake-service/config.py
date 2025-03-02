import os
from typing import List, Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/app/uploads")
    PROCESSING_SERVICE_URL: str = os.getenv("PROCESSING_SERVICE_URL", "http://cv-processing-service:8001")
    STORAGE_SERVICE_URL: str = os.getenv("STORAGE_SERVICE_URL", "http://cv-storage-service:8002")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_JOB_PREFIX: str = os.getenv("REDIS_JOB_PREFIX", "cv:job:")
    JOB_RETENTION_DAYS: int = int(os.getenv("JOB_RETENTION_DAYS", "30"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ALLOWED_FILE_EXTENSIONS: List[str] = [".pdf", ".jpg", ".jpeg", ".png"]

    # File storage configuration
    TEMP_DIR: str = os.getenv("TEMP_DIR", "/tmp/cv_uploads")
    DURABLE_STORAGE: Literal["local", "s3", "none"] = os.getenv("DURABLE_STORAGE", "none")

    # S3 settings (only used when DURABLE_STORAGE is "s3")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    S3_ENDPOINT_URL: str = os.getenv("S3_ENDPOINT_URL", "")  # For non-AWS S3 compatible services


settings = Settings()