from typing import List, Literal, Optional
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Service configuration
    SERVICE_NAME: str = "cv-intake-service"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    PORT: int = 8000

    # File handling
    UPLOAD_DIR: str = "/app/uploads"
    TEMP_DIR: str = "/tmp/cv_uploads"
    ALLOWED_FILE_EXTENSIONS: List[str] = [".pdf", ".jpg", ".jpeg", ".png"]

    # File validation settings
    MAX_FILE_SIZE: int = 10485760  # 10MB
    MIN_FILE_SIZE: int = 1024  # 1KB

    # Security settings
    API_KEY: str = Field(..., description="API key for authentication")
    JWT_SECRET: str = Field(..., description="JWT secret key")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Rate limiting
    RATE_LIMIT_UPLOAD: str = "5/minute"
    RATE_LIMIT_STATUS: str = "30/minute"
    RATE_LIMIT_RESULTS: str = "20/minute"

    # Redis job queue configuration
    REDIS_JOB_QUEUE: str = "cv_processing_queue"
    REDIS_CLEANUP_QUEUE: str = "cv_cleanup_queue"
    REDIS_JOB_TIMEOUT: int = Field(default=1800, ge=300, le=3600)  # 30 minutes
    REDIS_WORKER_TIMEOUT: int = Field(default=30, ge=5, le=300)  # 30 seconds
    REDIS_MAX_RETRIES: int = Field(default=3, ge=1, le=10)

    # Async processing
    ENABLE_ASYNC_PROCESSING: bool = True
    ASYNC_PROCESSING_TIMEOUT: int = Field(default=300, ge=60, le=600)  # 5 minutes

    # File storage configuration
    DURABLE_STORAGE: Literal["local", "s3", "none"] = "none"

    # Service URLs - required
    PROCESSING_SERVICE_URL: str = Field(
        ..., description="URL of the CV processing service"
    )
    STORAGE_SERVICE_URL: str = Field(..., description="URL of the CV storage service")

    # Redis configuration - required
    REDIS_HOST: str = Field(..., description="Redis host")
    REDIS_PORT: int = Field(default=6379, ge=1, le=65535)
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    REDIS_JOB_PREFIX: str = "cv:job:"
    JOB_RETENTION_DAYS: int = Field(default=30, ge=1, le=365)

    # Database configuration
    NEO4J_URI: Optional[str] = Field(default=None, description="Neo4j database URI")
    QDRANT_HOST: Optional[str] = Field(
        default=None, description="Qdrant vector database host"
    )

    # S3 settings (only used when DURABLE_STORAGE is "s3")
    S3_BUCKET_NAME: Optional[str] = None
    S3_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None

    @model_validator(mode="after")
    def validate_durable_storage(self):
        if self.DURABLE_STORAGE == "s3":
            required_s3_fields = [
                ("S3_BUCKET_NAME", self.S3_BUCKET_NAME),
                ("AWS_ACCESS_KEY_ID", self.AWS_ACCESS_KEY_ID),
                ("AWS_SECRET_ACCESS_KEY", self.AWS_SECRET_ACCESS_KEY),
            ]
            for field_name, field_value in required_s3_fields:
                if not field_value:
                    raise ValueError(
                        f"When DURABLE_STORAGE is 's3', {field_name} must be provided"
                    )
        return self

    @field_validator("REDIS_PASSWORD")
    @classmethod
    def validate_redis_password(cls, v):
        if v == "":
            return None
        return v

    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret(cls, v):
        if not v or len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")
        return v

    @field_validator("API_KEY")
    @classmethod
    def validate_api_key(cls, v):
        if not v or len(v) < 16:
            raise ValueError("API_KEY must be at least 16 characters long")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance - will use environment variables or defaults
settings = Settings()  # type: ignore[call-arg]
