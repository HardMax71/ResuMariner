import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Service info
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "cv-storage-service")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Neo4j settings
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "testpassword")

    # Qdrant settings
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "qdrant")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "cv_key_points")
    VECTOR_SIZE: int = int(os.getenv("VECTOR_SIZE", "384"))  # Default dimension for all-MiniLM-L6-v2

    class Config:
        env_file = ".env"
        case_sensitive = True


# Initialize settings once
settings = Settings()
