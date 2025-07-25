from typing import Optional, Literal
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Service configuration
    SERVICE_NAME: str = "cv-processing-service"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    PORT: int = 8001

    # Service URLs
    STORAGE_SERVICE_URL: str = Field(
        default="http://cv-storage-service:8002",
        description="URL of the CV storage service",
    )

    # Core LLM Configuration - required
    LLM_PROVIDER: Literal["openai", "anthropic", "azure"] = "openai"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_API_KEY: str = Field(..., description="API key for LLM provider")
    LLM_BASE_URL: Optional[str] = Field(
        default=None, description="Custom base URL for LLM provider"
    )

    # Processing configuration
    PARALLEL_PROCESSING: bool = False
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    MAX_TOKENS_IN_RESUME_TO_PROCESS: int = 30000

    # Performance settings
    TEMPERATURE: float = Field(default=0.0, ge=0.0, le=2.0)
    REQUEST_TIMEOUT: int = Field(default=180, ge=30, le=600)
    MAX_RETRIES: int = Field(default=3, ge=1, le=10)

    @validator("LLM_API_KEY")
    def validate_llm_api_key(cls, v):
        if not v or v.strip() == "":
            raise ValueError("LLM_API_KEY is required and cannot be empty")
        return v.strip()

    @validator("LLM_BASE_URL")
    def validate_llm_base_url(cls, v):
        if v == "":
            return None
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()  # type: ignore[call-arg]
