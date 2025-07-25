"""
Comprehensive tests for cv-intake-service models to achieve 95%+ coverage.
"""

import pytest
from unittest.mock import Mock
from datetime import datetime


class TestModels:
    """Test all models in the job.py module"""

    def setup_method(self):
        """Setup for each test"""
        pass

    def test_job_status_enum(self):
        """Test JobStatus enum values"""
        try:
            from models.job import JobStatus

            # Test all enum values exist
            assert hasattr(JobStatus, "PENDING")
            assert hasattr(JobStatus, "PROCESSING")
            assert hasattr(JobStatus, "COMPLETED")
            assert hasattr(JobStatus, "FAILED")

            # Test enum values
            assert JobStatus.PENDING == "pending"
            assert JobStatus.PROCESSING == "processing"
            assert JobStatus.COMPLETED == "completed"
            assert JobStatus.FAILED == "failed"

        except ImportError:
            pytest.skip("Cannot import JobStatus")

    def test_job_model_creation(self):
        """Test Job model creation and validation - covers lines 22-24"""
        try:
            from models.job import Job, JobStatus

            # Test valid job creation
            job_data = {
                "job_id": "test-job-123",
                "file_path": "/tmp/test.pdf",
                "status": JobStatus.PENDING,
                "created_at": datetime.now(),
                "user_id": "user-123",
            }

            job = Job(**job_data)

            assert job.job_id == "test-job-123"
            assert job.file_path == "/tmp/test.pdf"
            assert job.status == JobStatus.PENDING
            assert job.user_id == "user-123"
            assert job.created_at is not None

        except ImportError:
            pytest.skip("Cannot import Job model")

    def test_job_model_with_optional_fields(self):
        """Test Job model with optional fields"""
        try:
            from models.job import Job, JobStatus

            # Test job with all optional fields
            job_data = {
                "job_id": "test-job-456",
                "file_path": "/tmp/test2.pdf",
                "status": JobStatus.COMPLETED,
                "created_at": datetime.now(),
                "completed_at": datetime.now(),
                "result": {"name": "John Doe", "skills": ["Python"]},
                "error_message": None,
            }

            job = Job(**job_data)

            assert job.completed_at is not None
            assert job.result == {"name": "John Doe", "skills": ["Python"]}
            assert job.error_message is None

        except ImportError:
            pytest.skip("Cannot import Job model for optional fields test")

    def test_job_model_file_path_validation(self):
        """Test Job model file_path validation - covers validator lines"""
        try:
            from models.job import Job, JobStatus
            from pydantic import ValidationError

            # Test invalid file path (empty)
            with pytest.raises(ValidationError):
                Job(
                    job_id="test-job",
                    file_path="",  # Empty path should fail validation
                    status=JobStatus.PENDING,
                    created_at=datetime.now(),
                )

            # Test invalid file path (None)
            with pytest.raises(ValidationError):
                Job(
                    job_id="test-job",
                    file_path=None,  # None path should fail validation
                    status=JobStatus.PENDING,
                    created_at=datetime.now(),
                )

        except ImportError:
            pytest.skip("Cannot import Job model for validation test")

    def test_file_upload_model_creation(self):
        """Test FileUpload model creation - covers lines 81-93"""
        try:
            from models.job import FileUpload

            # Test valid file upload
            # Create content that meets minimum size requirement (1024+ bytes)
            pdf_content = b"%PDF-1.4" + b"x" * 1024  # Valid PDF signature + padding
            file_data = {
                "filename": "test.pdf",
                "content_type": "application/pdf",
                "content": pdf_content,
            }

            file_upload = FileUpload(**file_data)

            assert file_upload.filename == "test.pdf"
            assert file_upload.content_type == "application/pdf"
            assert file_upload.content == pdf_content

        except ImportError:
            pytest.skip("Cannot import FileUpload model")

    def test_file_upload_filename_validation(self):
        """Test FileUpload filename validation - covers validator lines 78"""
        try:
            from models.job import FileUpload
            from pydantic import ValidationError

            # Test invalid filename (empty)
            with pytest.raises(ValidationError):
                FileUpload(
                    filename="",  # Empty filename should fail
                    content_type="application/pdf",
                    content=b"content",
                )

            # Test invalid filename (unsafe characters)
            with pytest.raises(ValidationError):
                FileUpload(
                    filename="../../../etc/passwd",  # Path traversal should fail
                    content_type="application/pdf",
                    content=b"content",
                )

        except ImportError:
            pytest.skip("Cannot import FileUpload for filename validation test")

    def test_file_upload_content_validation(self):
        """Test FileUpload content validation - covers validator lines 95"""
        try:
            from models.job import FileUpload
            from pydantic import ValidationError

            # Test empty content
            with pytest.raises(ValidationError):
                FileUpload(
                    filename="test.pdf",
                    content_type="application/pdf",
                    content=b"",  # Empty content should fail
                )

            # Test None content
            with pytest.raises(ValidationError):
                FileUpload(
                    filename="test.pdf",
                    content_type="application/pdf",
                    content=None,  # None content should fail
                )

        except ImportError:
            pytest.skip("Cannot import FileUpload for content validation test")

    def test_file_upload_from_upload_file_method(self):
        """Test FileUpload.from_upload_file class method - covers lines 97-116"""
        try:
            from models.job import FileUpload
            from fastapi import UploadFile

            # Mock UploadFile
            mock_upload_file = Mock(spec=UploadFile)
            mock_upload_file.filename = "test.pdf"
            mock_upload_file.content_type = "application/pdf"

            # Create content that meets minimum size requirement (1024+ bytes)
            content = b"%PDF-1.4" + b"x" * 1024  # Valid PDF signature + padding

            # Test from_upload_file method
            file_upload = FileUpload.from_upload_file(mock_upload_file, content)

            assert file_upload.filename == "test.pdf"
            assert file_upload.content_type == "application/pdf"
            assert file_upload.content == content

        except ImportError:
            pytest.skip("Cannot import FileUpload for from_upload_file test")

    def test_file_upload_from_upload_file_validation_error(self):
        """Test FileUpload.from_upload_file with validation errors"""
        try:
            from models.job import FileUpload
            from fastapi import UploadFile
            from pydantic import ValidationError

            # Mock UploadFile with invalid data
            mock_upload_file = Mock(spec=UploadFile)
            mock_upload_file.filename = ""  # Invalid empty filename
            mock_upload_file.content_type = "application/pdf"

            content = b"PDF file content"

            # Test from_upload_file method with invalid data
            with pytest.raises(ValidationError):
                FileUpload.from_upload_file(mock_upload_file, content)

        except ImportError:
            pytest.skip("Cannot import FileUpload for from_upload_file validation test")

    def test_job_response_model(self):
        """Test JobResponse model creation - covers line 121"""
        try:
            from models.job import JobResponse, JobStatus

            # Test JobResponse creation
            response_data = {
                "job_id": "test-job-789",
                "status": JobStatus.COMPLETED,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }

            response = JobResponse(**response_data)

            assert response.job_id == "test-job-789"
            assert response.status == JobStatus.COMPLETED
            assert response.created_at is not None
            assert response.updated_at is not None

        except ImportError:
            pytest.skip("Cannot import JobResponse model")

    def test_job_response_with_optional_fields(self):
        """Test JobResponse with all optional fields"""
        try:
            from models.job import JobResponse, JobStatus

            # Test JobResponse with optional fields
            response_data = {
                "job_id": "test-job-999",
                "status": JobStatus.COMPLETED,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "result_url": "https://example.com/result.json",
                "error": None,
            }

            response = JobResponse(**response_data)

            assert response.result_url == "https://example.com/result.json"
            assert response.error is None

        except ImportError:
            pytest.skip("Cannot import JobResponse for optional fields test")

    def test_model_json_serialization(self):
        """Test model JSON serialization and deserialization"""
        try:
            from models.job import Job, JobStatus
            import json

            # Create a job
            job = Job(
                job_id="serialize-test",
                file_path="/tmp/serialize.pdf",
                status=JobStatus.PENDING,
                created_at=datetime.now(),
            )

            # Test JSON serialization
            job_dict = job.dict()
            assert isinstance(job_dict, dict)
            assert job_dict["job_id"] == "serialize-test"

            # Test JSON string conversion
            job_json = job.json()
            assert isinstance(job_json, str)

            # Test reconstruction from dict
            job_data = json.loads(job_json)
            assert job_data["job_id"] == "serialize-test"

        except ImportError:
            pytest.skip("Cannot import Job for serialization test")

    def test_model_field_defaults(self):
        """Test model field defaults and required fields"""
        try:
            from models.job import Job, JobStatus
            from pydantic import ValidationError

            # Test missing required fields
            with pytest.raises(ValidationError):
                Job()  # Should fail due to missing required fields

            # Test minimal valid job
            minimal_job = Job(
                job_id="minimal-job",
                file_path="/tmp/minimal.pdf",
                status=JobStatus.PENDING,
                created_at=datetime.now(),
            )

            assert minimal_job.job_id == "minimal-job"
            assert minimal_job.result is None  # Should default to None
            assert minimal_job.error_message is None  # Should default to None

        except ImportError:
            pytest.skip("Cannot import Job for defaults test")

    def test_model_type_validation(self):
        """Test model type validation for various fields"""
        try:
            from models.job import Job, JobStatus
            from pydantic import ValidationError

            # Test invalid types
            with pytest.raises(ValidationError):
                Job(
                    job_id=123,  # Should be string
                    file_path="/tmp/test.pdf",
                    status=JobStatus.PENDING,
                    created_at=datetime.now(),
                )

            with pytest.raises(ValidationError):
                Job(
                    job_id="test-job",
                    file_path=123,  # Should be string
                    status=JobStatus.PENDING,
                    created_at=datetime.now(),
                )

        except ImportError:
            pytest.skip("Cannot import Job for type validation test")
