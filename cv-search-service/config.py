from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration settings loaded from environment variables"""

    # Service info
    SERVICE_NAME: str = "cv-search-service"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    PORT: int = 8003

    # Database connections - required
    NEO4J_URI: str = Field(..., description="Neo4j connection URI")
    NEO4J_USERNAME: str = Field(..., description="Neo4j username")
    NEO4J_PASSWORD: str = Field(..., description="Neo4j password")
    NEO4J_DATABASE: str = "neo4j"

    # Neo4j connection pooling
    NEO4J_MAX_CONNECTION_LIFETIME: int = Field(default=3600, ge=300, le=86400)
    NEO4J_MAX_CONNECTION_POOL_SIZE: int = Field(default=50, ge=1, le=200)
    NEO4J_CONNECTION_TIMEOUT: int = Field(default=30, ge=5, le=300)

    # Qdrant configuration
    QDRANT_HOST: str = Field(default="qdrant", description="Qdrant host")
    QDRANT_PORT: int = Field(default=6333, ge=1, le=65535)
    QDRANT_COLLECTION: str = "cv_key_points"
    QDRANT_TIMEOUT: int = Field(default=30, ge=5, le=300)
    QDRANT_PREFER_GRPC: bool = True

    # Embedding model settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    VECTOR_SIZE: int = Field(default=384, ge=128, le=4096)

    # Search settings
    DEFAULT_VECTOR_WEIGHT: float = Field(default=0.7, ge=0.0, le=1.0)
    DEFAULT_GRAPH_WEIGHT: float = Field(default=0.3, ge=0.0, le=1.0)

    # Performance
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = Field(default=3600, ge=60, le=86400)

    # Security settings
    API_KEY: str = Field(..., description="API key for authentication")
    JWT_SECRET: str = Field(..., description="JWT secret key")
    JWT_ALGORITHM: str = "HS256"

    # Rate limiting
    RATE_LIMIT_SEARCH: str = "20/minute"
    RATE_LIMIT_SUGGEST: str = "30/minute"

    @validator("NEO4J_PASSWORD")
    def validate_neo4j_password(cls, v):
        if not v or v.strip() == "":
            raise ValueError("NEO4J_PASSWORD is required and cannot be empty")
        return v.strip()

    @validator("DEFAULT_GRAPH_WEIGHT")
    def validate_weights_sum(cls, v, values):
        if "DEFAULT_VECTOR_WEIGHT" in values:
            vector_weight = values["DEFAULT_VECTOR_WEIGHT"]
            if abs(vector_weight + v - 1.0) > 0.001:
                raise ValueError("Vector weight and graph weight must sum to 1.0")
        return v

    @validator("JWT_SECRET")
    def validate_jwt_secret(cls, v):
        if not v or len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")
        return v

    @validator("API_KEY")
    def validate_api_key(cls, v):
        if not v or len(v) < 16:
            raise ValueError("API_KEY must be at least 16 characters long")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()  # type: ignore[call-arg]
