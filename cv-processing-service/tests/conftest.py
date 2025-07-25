"""
Configuration for pytest in cv-processing-service.
"""

import os
from pathlib import Path

# Set environment variables for testing
os.environ.update(
    {
        "ENVIRONMENT": "testing",
        "DEBUG": "true",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "testpass",
        "QDRANT_HOST": "localhost",
        "QDRANT_PORT": "6333",
        "OPENAI_API_KEY": "sk-test-key-1234567890123456789012345678901234567890",
        "LLM_API_KEY": "sk-test-llm-key-1234567890123456789012345678901234567890",
        "JWT_SECRET": "test-jwt-secret-key-that-is-at-least-32-characters-long-for-validation",
        "API_KEY": "test-api-key-that-is-at-least-16-characters-long",
        "UPLOAD_DIR": "/tmp/test_uploads",
        "DURABLE_STORAGE": "local",
    }
)
