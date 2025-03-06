import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Service URLs
    PROCESSING_SERVICE_URL: str = os.getenv("PROCESSING_SERVICE_URL", "http://cv-processing-service:8001")
    STORAGE_SERVICE_URL: str = os.getenv("STORAGE_SERVICE_URL", "http://cv-storage-service:8002")

    # Core LLM Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "")

    # Service configuration
    PARALLEL_PROCESSING: bool = os.getenv("PARALLEL_PROCESSING", "false").lower() == "true"
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    MAX_TOKENS_IN_RESUME_TO_PROCESS: int = 30_000

    # Performance settings
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.0"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "180"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))

    # Debug settings
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"


settings = Settings()
