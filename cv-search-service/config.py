import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration settings loaded from environment variables"""
    # Service info
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "cv-search-service")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    PORT: int = int(os.getenv("PORT", "8003"))

    # Database connections
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "testpassword")
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "qdrant")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "cv_key_points")

    # Embedding model settings
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    VECTOR_SIZE: int = int(os.getenv("VECTOR_SIZE", "384"))

    # Search settings
    DEFAULT_VECTOR_WEIGHT: float = float(os.getenv("DEFAULT_VECTOR_WEIGHT", "0.7"))
    DEFAULT_GRAPH_WEIGHT: float = float(os.getenv("DEFAULT_GRAPH_WEIGHT", "0.3"))

    # Performance
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
