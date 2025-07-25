"""Comprehensive tests for cv-processing-service routes to achieve 95%+ coverage."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from io import BytesIO


class TestProcessingRoutes:
    """Test cv-processing-service routes"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        with patch("config.settings") as mock_settings:
            mock_settings.LLM_PROVIDER = "openai"
            mock_settings.LLM_MODEL = "gpt-4o-mini"
            mock_settings.DEBUG = False

            from app import app

            return TestClient(app)

    @pytest.fixture
    def mock_processing_service(self):
        """Mock processing service"""
        with patch("routes.processing_routes.processing_service") as mock:
            yield mock

    @pytest.fixture
    def sample_pdf_file(self):
        """Create a sample PDF file for testing"""
        return ("test.pdf", b"fake PDF content", "application/pdf")

    @pytest.fixture
    def sample_image_file(self):
        """Create a sample image file for testing"""
        return ("test.jpg", b"fake image content", "image/jpeg")

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "llm_provider" in data
        assert "llm_model" in data

    @patch("routes.processing_routes.processing_service")
    def test_process_cv_success_pdf(
        self, mock_processing_service, client, sample_pdf_file
    ):
        """Test successful CV processing with PDF file"""
        # Mock the processing service response
        mock_result = {
            "structured_data": {"name": "John Doe", "skills": ["Python"]},
            "review": {"score": 85, "feedback": "Good candidate"},
            "processing_time": 12.5,
            "metadata": {"parser": "pdf", "pages": 2},
        }
        mock_processing_service.process_file = AsyncMock(return_value=mock_result)

        filename, content, content_type = sample_pdf_file
        files = {"file": (filename, BytesIO(content), content_type)}
        data = {"parallel": "false", "generate_review": "true", "store_in_db": "true"}

        response = client.post("/process", files=files, data=data)

        assert response.status_code == 200
        result = response.json()
        assert result["structured_data"]["name"] == "John Doe"
        assert result["review"]["score"] == 85
        assert result["processing_time"] == 12.5

    @patch("routes.processing_routes.processing_service")
    def test_process_cv_success_image(
        self, mock_processing_service, client, sample_image_file
    ):
        """Test successful CV processing with image file"""
        mock_result = {
            "structured_data": {"name": "Jane Smith", "skills": ["Java"]},
            "review": None,
            "processing_time": 8.3,
            "metadata": {"parser": "image"},
        }
        mock_processing_service.process_file = AsyncMock(return_value=mock_result)

        filename, content, content_type = sample_image_file
        files = {"file": (filename, BytesIO(content), content_type)}
        data = {"parallel": "true", "generate_review": "false", "store_in_db": "false"}

        response = client.post("/process", files=files, data=data)

        assert response.status_code == 200
        result = response.json()
        assert result["structured_data"]["name"] == "Jane Smith"
        assert result["review"] is None
        assert result["processing_time"] == 8.3

    def test_process_cv_no_file(self, client):
        """Test processing without file upload"""
        data = {"parallel": "false", "generate_review": "true", "store_in_db": "true"}

        response = client.post("/process", data=data)

        assert response.status_code == 422  # Validation error

    @patch("routes.processing_routes.processing_service")
    def test_process_cv_file_no_filename(self, mock_processing_service, client):
        """Test processing with file that has no filename"""
        files = {"file": (None, BytesIO(b"content"), "application/pdf")}
        data = {"parallel": "false", "generate_review": "true", "store_in_db": "true"}

        response = client.post("/process", files=files, data=data)

        assert response.status_code == 500
        assert "Processing failed" in response.json()["detail"]

    @patch("routes.processing_routes.processing_service")
    def test_process_cv_processing_service_http_exception(
        self, mock_processing_service, client, sample_pdf_file
    ):
        """Test processing when service raises HTTPException"""
        mock_processing_service.process_file = AsyncMock(
            side_effect=HTTPException(status_code=400, detail="Invalid file format")
        )

        filename, content, content_type = sample_pdf_file
        files = {"file": (filename, BytesIO(content), content_type)}
        data = {"parallel": "false", "generate_review": "true", "store_in_db": "true"}

        response = client.post("/process", files=files, data=data)

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid file format"

    @patch("routes.processing_routes.processing_service")
    def test_process_cv_processing_service_generic_exception(
        self, mock_processing_service, client, sample_pdf_file
    ):
        """Test processing when service raises generic exception"""
        mock_processing_service.process_file = AsyncMock(
            side_effect=Exception("Processing service failed")
        )

        filename, content, content_type = sample_pdf_file
        files = {"file": (filename, BytesIO(content), content_type)}
        data = {"parallel": "false", "generate_review": "true", "store_in_db": "true"}

        response = client.post("/process", files=files, data=data)

        assert response.status_code == 500
        assert "Processing failed" in response.json()["detail"]
        assert "Processing service failed" in response.json()["detail"]

    @patch("routes.processing_routes.processing_service")
    @patch("os.path.exists")
    @patch("os.unlink")
    def test_process_cv_temp_file_cleanup_success(
        self, mock_unlink, mock_exists, mock_processing_service, client, sample_pdf_file
    ):
        """Test temp file cleanup on successful processing"""
        mock_exists.return_value = True
        mock_processing_service.process_file = AsyncMock(
            return_value={
                "structured_data": {"name": "Test"},
                "processing_time": 1.0,
                "metadata": {},
            }
        )

        filename, content, content_type = sample_pdf_file
        files = {"file": (filename, BytesIO(content), content_type)}
        data = {"parallel": "false", "generate_review": "true", "store_in_db": "true"}

        response = client.post("/process", files=files, data=data)

        assert response.status_code == 200
        mock_unlink.assert_called_once()

    @patch("routes.processing_routes.processing_service")
    @patch("os.path.exists")
    @patch("os.unlink")
    def test_process_cv_temp_file_cleanup_on_error(
        self, mock_unlink, mock_exists, mock_processing_service, client, sample_pdf_file
    ):
        """Test temp file cleanup on processing error"""
        mock_exists.return_value = True
        mock_processing_service.process_file = AsyncMock(
            side_effect=Exception("Processing failed")
        )

        filename, content, content_type = sample_pdf_file
        files = {"file": (filename, BytesIO(content), content_type)}
        data = {"parallel": "false", "generate_review": "true", "store_in_db": "true"}

        response = client.post("/process", files=files, data=data)

        assert response.status_code == 500
        mock_unlink.assert_called_once()

    @patch("routes.processing_routes.processing_service")
    @patch("os.path.exists")
    @patch("os.unlink")
    def test_process_cv_temp_file_cleanup_file_not_exists(
        self, mock_unlink, mock_exists, mock_processing_service, client, sample_pdf_file
    ):
        """Test temp file cleanup when file doesn't exist"""
        mock_exists.return_value = False
        mock_processing_service.process_file = AsyncMock(
            return_value={
                "structured_data": {"name": "Test"},
                "processing_time": 1.0,
                "metadata": {},
            }
        )

        filename, content, content_type = sample_pdf_file
        files = {"file": (filename, BytesIO(content), content_type)}
        data = {"parallel": "false", "generate_review": "true", "store_in_db": "true"}

        response = client.post("/process", files=files, data=data)

        assert response.status_code == 200
        mock_unlink.assert_not_called()

    @patch("routes.processing_routes.processing_service")
    def test_process_cv_different_form_options(
        self, mock_processing_service, client, sample_pdf_file
    ):
        """Test processing with different form option combinations"""
        mock_processing_service.process_file = AsyncMock(
            return_value={
                "structured_data": {"name": "Test"},
                "processing_time": 1.0,
                "metadata": {},
            }
        )

        filename, content, content_type = sample_pdf_file

        # Test all combinations of boolean options
        option_combinations = [
            {"parallel": "true", "generate_review": "true", "store_in_db": "true"},
            {"parallel": "false", "generate_review": "false", "store_in_db": "false"},
            {"parallel": "true", "generate_review": "false", "store_in_db": "true"},
            {"parallel": "false", "generate_review": "true", "store_in_db": "false"},
        ]

        for options in option_combinations:
            files = {"file": (filename, BytesIO(content), content_type)}
            response = client.post("/process", files=files, data=options)
            assert response.status_code == 200

    @patch("routes.processing_routes.processing_service")
    def test_process_cv_options_object_creation(
        self, mock_processing_service, client, sample_pdf_file
    ):
        """Test ProcessingOptions object is created correctly"""
        mock_processing_service.process_file = AsyncMock(
            return_value={
                "structured_data": {"name": "Test"},
                "processing_time": 1.0,
                "metadata": {},
            }
        )

        filename, content, content_type = sample_pdf_file
        files = {"file": (filename, BytesIO(content), content_type)}
        data = {"parallel": "true", "generate_review": "false", "store_in_db": "true"}

        response = client.post("/process", files=files, data=data)

        assert response.status_code == 200

        # Verify the ProcessingOptions object was created with correct values
        call_args = mock_processing_service.process_file.call_args
        options = call_args[0][2]  # Third argument is options

        assert options.parallel is True
        assert options.generate_review is False
        assert options.store_in_db is True

    @patch("routes.processing_routes.processing_service")
    @patch("tempfile.NamedTemporaryFile")
    def test_process_cv_temp_file_creation(
        self, mock_tempfile, mock_processing_service, client, sample_pdf_file
    ):
        """Test temp file creation with correct suffix"""
        mock_temp_file = MagicMock()
        mock_temp_file.name = "/tmp/test.pdf"
        mock_tempfile.return_value = mock_temp_file

        mock_processing_service.process_file = AsyncMock(
            return_value={
                "structured_data": {"name": "Test"},
                "processing_time": 1.0,
                "metadata": {},
            }
        )

        filename, content, content_type = sample_pdf_file
        files = {"file": (filename, BytesIO(content), content_type)}
        data = {"parallel": "false", "generate_review": "true", "store_in_db": "true"}

        client.post("/process", files=files, data=data)

        # Verify temp file was created with correct suffix
        mock_tempfile.assert_called_once_with(delete=False, suffix=".pdf")
        mock_temp_file.write.assert_called_once_with(content)
        mock_temp_file.close.assert_called_once()

    def test_process_cv_different_file_extensions(self, client):
        """Test processing with different file extensions"""
        file_types = [
            ("test.pdf", b"pdf content", "application/pdf"),
            ("test.jpg", b"jpg content", "image/jpeg"),
            ("test.png", b"png content", "image/png"),
            ("test.jpeg", b"jpeg content", "image/jpeg"),
        ]

        with patch("routes.processing_routes.processing_service") as mock_service:
            mock_service.process_file = AsyncMock(
                return_value={
                    "structured_data": {"name": "Test"},
                    "processing_time": 1.0,
                    "metadata": {},
                }
            )

            for filename, content, content_type in file_types:
                files = {"file": (filename, BytesIO(content), content_type)}
                data = {
                    "parallel": "false",
                    "generate_review": "true",
                    "store_in_db": "true",
                }

                response = client.post("/process", files=files, data=data)
                assert response.status_code == 200

    @patch("routes.processing_routes.logger")
    @patch("routes.processing_routes.processing_service")
    def test_process_cv_error_logging(
        self, mock_processing_service, mock_logger, client, sample_pdf_file
    ):
        """Test error logging in process_cv endpoint"""
        mock_processing_service.process_file = AsyncMock(
            side_effect=Exception("Test error for logging")
        )

        filename, content, content_type = sample_pdf_file
        files = {"file": (filename, BytesIO(content), content_type)}
        data = {"parallel": "false", "generate_review": "true", "store_in_db": "true"}

        response = client.post("/process", files=files, data=data)

        assert response.status_code == 500
        mock_logger.error.assert_called_once()
        error_message = mock_logger.error.call_args[0][0]
        assert "Error processing file" in error_message
        assert "Test error for logging" in error_message

    def test_router_instance_creation(self):
        """Test router instance is created"""
        from routes.processing_routes import router

        assert router is not None
        assert hasattr(router, "routes")

    def test_processing_service_instance_creation(self):
        """Test processing service instance is created"""
        from routes.processing_routes import processing_service

        assert processing_service is not None

    @patch("config.settings")
    def test_health_endpoint_different_settings(self, mock_settings, client):
        """Test health endpoint with different LLM settings"""
        test_cases = [
            {"LLM_PROVIDER": "openai", "LLM_MODEL": "gpt-4"},
            {"LLM_PROVIDER": "anthropic", "LLM_MODEL": "claude-3-sonnet"},
            {"LLM_PROVIDER": "azure", "LLM_MODEL": "gpt-35-turbo"},
        ]

        for settings_config in test_cases:
            mock_settings.LLM_PROVIDER = settings_config["LLM_PROVIDER"]
            mock_settings.LLM_MODEL = settings_config["LLM_MODEL"]

            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["llm_provider"] == settings_config["LLM_PROVIDER"]
            assert data["llm_model"] == settings_config["LLM_MODEL"]

    def test_process_cv_response_model_validation(self, client):
        """Test that response follows ProcessingResult model"""
        with patch("routes.processing_routes.processing_service") as mock_service:
            # Return data that matches ProcessingResult model
            mock_service.process_file = AsyncMock(
                return_value={
                    "structured_data": {"name": "Test User"},
                    "review": {"score": 85},
                    "processing_time": 5.5,
                    "metadata": {"source": "test"},
                }
            )

            files = {"file": ("test.pdf", BytesIO(b"content"), "application/pdf")}
            data = {
                "parallel": "false",
                "generate_review": "true",
                "store_in_db": "true",
            }

            response = client.post("/process", files=files, data=data)

            assert response.status_code == 200
            result = response.json()

            # Verify all required fields are present
            assert "structured_data" in result
            assert "processing_time" in result
            assert "metadata" in result
            # review can be null, so check if present
            assert "review" in result
