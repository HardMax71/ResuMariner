from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Service info
    SERVICE_NAME: str = "cv-storage-service"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    PORT: int = 8002

    # Neo4j settings - required
    NEO4J_URI: str = Field(..., description="Neo4j connection URI")
    NEO4J_USERNAME: str = Field(..., description="Neo4j username")
    NEO4J_PASSWORD: str = Field(..., description="Neo4j password")
    NEO4J_DATABASE: str = "neo4j"

    # Neo4j connection pooling
    NEO4J_MAX_CONNECTION_LIFETIME: int = Field(default=3600, ge=300, le=86400)
    NEO4J_MAX_CONNECTION_POOL_SIZE: int = Field(default=50, ge=1, le=200)
    NEO4J_CONNECTION_TIMEOUT: int = Field(default=30, ge=5, le=300)

    # Qdrant settings
    QDRANT_HOST: str = Field(default="qdrant", description="Qdrant host")
    QDRANT_PORT: int = Field(default=6333, ge=1, le=65535)
    QDRANT_COLLECTION: str = "cv_key_points"
    VECTOR_SIZE: int = Field(default=384, ge=128, le=4096)
    QDRANT_TIMEOUT: int = Field(default=30, ge=5, le=300)
    QDRANT_PREFER_GRPC: bool = True

    @validator("NEO4J_PASSWORD")
    def validate_neo4j_password(cls, v):
        if not v or v.strip() == "":
            raise ValueError("NEO4J_PASSWORD is required and cannot be empty")
        return v.strip()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()  # type: ignore[call-arg]
