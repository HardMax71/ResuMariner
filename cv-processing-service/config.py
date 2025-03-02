import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROCESSING_SERVICE_URL: str = os.getenv("PROCESSING_SERVICE_URL", "http://cv-processing-service:8001")
    STORAGE_SERVICE_URL: str = os.getenv("STORAGE_SERVICE_URL", "http://cv-storage-service:8002")

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", 'GROQ_DEADBEEF')
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', 'GEMINI_DEADBEEF')
    COHERE_API_KEY: str = os.getenv('COHERE_API_KEY', 'COHERE_DEADBEEF')
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', "OPENAI_DEADBEEF")

    API_KEY: str = OPENAI_API_KEY # the one that is used, all other - for model testing

    # Service configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")  # openai, gemini, groq, cohere
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    PARALLEL_PROCESSING: bool = os.getenv("PARALLEL_PROCESSING", "false").lower() == "true"
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    MAX_TOKENS_IN_RESUME_TO_PROCESS: int = 30_000

    # Performance settings
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.0"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "180"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))

    # Debug settings
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    @property
    def active_api_key(self) -> str:
        """Return the appropriate API key based on selected provider"""
        return self.API_KEY

        # if self.LLM_PROVIDER == "openai":
        #     return self.OPENAI_API_KEY
        # elif self.LLM_PROVIDER == "gemini":
        #     return self.GEMINI_API_KEY
        # elif self.LLM_PROVIDER == "groq":
        #     return self.GROQ_API_KEY
        # elif self.LLM_PROVIDER == "cohere":
        #     return self.COHERE_API_KEY
        # return self.OPENAI_API_KEY

settings = Settings()