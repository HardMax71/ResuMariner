"""
Pytest configuration and fixtures for cv-intake-service tests.
"""

import pytest
import os
from unittest.mock import patch

# Set required environment variables before any module imports
os.environ.update(
    {
        "DEBUG": "true",
        "API_KEY": "test-api-key-16-characters-long",
        "JWT_SECRET": "test-jwt-secret-key-that-is-at-least-32-chars",
        "PROCESSING_SERVICE_URL": "http://cv-processing-service:8001",
        "STORAGE_SERVICE_URL": "http://cv-storage-service:8002",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "UPLOAD_DIR": "/tmp/test_uploads",
        "TEMP_DIR": "/tmp/cv_uploads",
    }
)


@pytest.fixture(autouse=True)
def clear_temp_files(request):
    """Automatically clear FileService temp files between tests to ensure isolation"""
    try:
        from services.file_service import FileService

        # Skip auto-clearing for tests that specifically test temp file functionality
        if hasattr(request.node, "name") and any(
            pattern in request.node.name.lower()
            for pattern in ["temp_file", "cleanup", "file_service_95_coverage"]
        ):
            yield
            return

        # Clear before test
        FileService.clear_temp_files()
        yield
        # Clear after test
        FileService.clear_temp_files()
    except ImportError:
        # If FileService can't be imported, just yield
        yield


@pytest.fixture(autouse=True)
def mock_external_services():
    """Mock external service calls to prevent real HTTP requests during testing"""
    with (
        patch("requests.get") as mock_get,
        patch("requests.post") as mock_post,
        patch("httpx.AsyncClient.get") as mock_async_get,
        patch("httpx.AsyncClient.post") as mock_async_post,
    ):
        # Mock successful health check responses
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"status": "healthy"}
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"status": "success"}

        # Mock async responses
        mock_async_get.return_value.status_code = 200
        mock_async_get.return_value.json.return_value = {"status": "healthy"}
        mock_async_post.return_value.status_code = 200
        mock_async_post.return_value.json.return_value = {"status": "success"}

        yield


@pytest.fixture(autouse=True)
def setup_test_metrics():
    """Ensure metrics registry is properly initialized for tests"""
    try:
        from prometheus_client import CollectorRegistry
        import prometheus_client

        # Store original registry
        original_registry = prometheus_client.REGISTRY

        # Create a fresh registry for each test
        test_registry = CollectorRegistry()
        prometheus_client.REGISTRY = test_registry

        yield

        # Restore original registry
        prometheus_client.REGISTRY = original_registry

    except ImportError:
        yield
