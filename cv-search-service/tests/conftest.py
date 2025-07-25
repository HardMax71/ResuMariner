"""
Configuration for pytest in cv-search-service.
"""

import os

# Set environment variables for testing
os.environ.update(
    {
        "ENVIRONMENT": "testing",
        "DEBUG": "true",
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "testpass",
        "QDRANT_HOST": "localhost",
        "QDRANT_PORT": "6333",
        "QDRANT_API_KEY": "test-qdrant-key-that-is-at-least-16-characters-long",
        "OPENAI_API_KEY": "sk-test-key-1234567890123456789012345678901234567890",
        "JWT_SECRET": "test-jwt-secret-key-that-is-at-least-32-characters-long-for-validation",
        "API_KEY": "test-api-key-that-is-at-least-16-characters-long",
    }
)
