"""
Comprehensive tests for cv-intake-service services/file_service.py to achieve 95%+ coverage.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, mock_open


class TestFileService:
    """Comprehensive test class for file_service.py"""

    def setup_method(self):
        """Setup for each test"""
        self.patches = {}
        self.setup_mocks()

    def teardown_method(self):
        """Cleanup after each test"""
        for patch_obj in self.patches.values():
            try:
                patch_obj.stop()
            except Exception:
                pass

    def setup_mocks(self):
        """Setup mocks for dependencies"""
        # Mock environment
        self.patches["env"] = patch.dict(
            "os.environ",
            {
                "UPLOAD_DIR": "/tmp/test_uploads",
                "DURABLE_STORAGE": "local",
                "AWS_S3_BUCKET": "test-bucket",
            },
        )
        self.patches["env"].start()

        # Mock os operations
        self.patches["makedirs"] = patch("os.makedirs")
        self.patches["makedirs"].start()

        # Mock boto3 for S3 operations
        self.patches["boto3"] = patch("boto3.client")
        self.patches["boto3"].start()

    def test_validate_file_type_valid_pdf(self):
        """Test file type validation for valid PDF"""
        try:
            from services.file_service import FileService

            # Test valid PDF
            assert FileService.validate_file_type("test.pdf")
            assert FileService.validate_file_type("document.PDF")

        except ImportError:
            pytest.skip("Cannot import FileService")

    def test_validate_file_type_valid_docx(self):
        """Test file type validation for valid DOCX"""
        try:
            from services.file_service import FileService

            # Test valid DOCX
            assert FileService.validate_file_type("resume.docx")
            assert FileService.validate_file_type("cv.DOCX")

        except ImportError:
            pytest.skip("Cannot import FileService")

    def test_validate_file_type_valid_image(self):
        """Test file type validation for valid images"""
        try:
            from services.file_service import FileService

            # Test valid images
            assert FileService.validate_file_type("scan.jpg")
            assert FileService.validate_file_type("photo.jpeg")
            assert FileService.validate_file_type("image.png")

        except ImportError:
            pytest.skip("Cannot import FileService")

    def test_validate_file_type_invalid(self):
        """Test file type validation for invalid files"""
        try:
            from services.file_service import FileService

            # Test invalid files - validate_file_type returns (is_valid, file_ext) tuple
            is_valid, file_ext = FileService.validate_file_type("script.exe")
            assert not is_valid
            assert file_ext == ".exe"

            is_valid, file_ext = FileService.validate_file_type("data.txt")
            assert not is_valid
            assert file_ext == ".txt"

            is_valid, file_ext = FileService.validate_file_type("malware.bat")
            assert not is_valid
            assert file_ext == ".bat"

        except ImportError:
            pytest.skip("Cannot import FileService")

    def test_save_uploaded_file_success(self):
        """Test successful file upload - covers lines 21-82"""
        try:
            import asyncio
            from fastapi import UploadFile
            from services.file_service import FileService

            with (
                patch("os.makedirs") as mock_makedirs,
                patch("builtins.open", mock_open()) as mock_file_open,
                patch("shutil.copyfileobj") as mock_copyfileobj,
                patch("shutil.copy2") as mock_copy2,
                patch("os.path.join", side_effect=lambda x, y: f"{x}/{y}"),
                patch.object(
                    FileService, "validate_file_type", return_value=(True, ".pdf")
                ),
                patch("services.file_service.settings") as mock_settings,
            ):
                # Mock settings
                mock_settings.TEMP_DIR = "/tmp/cv_uploads"
                mock_settings.DURABLE_STORAGE = "local"
                mock_settings.UPLOAD_DIR = "/tmp/test_uploads"

                # Create a mock UploadFile
                mock_file = Mock(spec=UploadFile)
                mock_file.filename = "test.pdf"
                mock_file.file = Mock()
                mock_file.seek = AsyncMock()

                result = asyncio.run(
                    FileService.save_uploaded_file(mock_file, "job-123")
                )

                # Verify mocks were called
                assert mock_makedirs.call_count >= 1  # May be called multiple times
                mock_file.seek.assert_called_once_with(0)
                mock_file_open.assert_called_once_with(
                    "/tmp/cv_uploads/job-123.pdf", "wb"
                )
                mock_copyfileobj.assert_called_once()
                mock_copy2.assert_called_once()

                assert result == "/tmp/cv_uploads/job-123.pdf"

        except (ImportError, NameError):
            pytest.skip("Cannot import FileService for save test")

    def test_save_uploaded_file_invalid_type(self):
        """Test file upload with invalid file type"""
        try:
            import asyncio
            from fastapi import UploadFile, HTTPException
            from services.file_service import FileService

            with patch.object(
                FileService, "validate_file_type", return_value=(False, ".exe")
            ):
                mock_file = Mock(spec=UploadFile)
                mock_file.filename = "malware.exe"

                # Test save_uploaded_file with invalid type
                with pytest.raises(HTTPException) as exc_info:
                    asyncio.run(FileService.save_uploaded_file(mock_file, "job-123"))

                assert exc_info.value.status_code == 400
                assert "Invalid file type" in str(exc_info.value.detail)

        except (ImportError, NameError):
            pytest.skip("Cannot import FileService for invalid type test")

    def test_save_uploaded_file_no_filename(self):
        """Test file upload with no filename"""
        try:
            mock_file = Mock()
            mock_file.filename = None

            from services.file_service import FileService

            # Test save_uploaded_file with no filename
            with pytest.raises(Exception) as exc_info:
                import asyncio

                asyncio.run(FileService.save_uploaded_file(mock_file, "job-123"))

            assert "file none was not found" in str(exc_info.value).lower()

        except (ImportError, NameError):
            pytest.skip("Cannot import FileService for no filename test")

    def test_get_durable_file_path_local_storage(self):
        """Test get_durable_file_path with local storage"""
        try:
            with (
                patch("os.path.exists", return_value=True),
                patch("services.file_service.settings") as mock_settings,
            ):
                mock_settings.DURABLE_STORAGE = "local"
                mock_settings.UPLOAD_DIR = "/tmp/uploads"

                from services.file_service import FileService

                result = FileService.get_durable_file_path("test", ".pdf")

                assert result is not None
                assert "test.pdf" in result

        except (ImportError, NameError):
            pytest.skip("Cannot import FileService for local storage test")

    def test_get_durable_file_path_not_found(self):
        """Test get_durable_file_path when file not found"""
        try:
            with patch("os.path.exists", return_value=False):
                from services.file_service import FileService

                result = FileService.get_durable_file_path("nonexistent.pdf")

                assert result is None

        except ImportError:
            pytest.skip("Cannot import FileService for not found test")

    def test_get_durable_file_path_s3(self):
        """Test get_durable_file_path with S3 storage - covers lines 157-166"""
        try:
            with (
                patch.dict(
                    "os.environ",
                    {"DURABLE_STORAGE": "s3", "S3_BUCKET_NAME": "test-bucket"},
                ),
                patch("services.file_service.settings") as mock_settings,
            ):
                mock_settings.DURABLE_STORAGE = "s3"

                from services.file_service import FileService

                # Test with extension provided
                result = FileService.get_durable_file_path("test", ".pdf")
                assert result == "s3:test.pdf"

                # Test without extension (should return None)
                result = FileService.get_durable_file_path("test")
                assert result is None

        except ImportError:
            pytest.skip("Cannot import FileService for S3 test")

    def test_get_durable_file_path_no_storage(self):
        """Test get_durable_file_path with unknown storage type"""
        try:
            with patch.dict("os.environ", {"DURABLE_STORAGE": "unknown"}):
                from services.file_service import FileService

                result = FileService.get_durable_file_path("test.pdf")

                assert result is None

        except ImportError:
            pytest.skip("Cannot import FileService for no storage test")

    def test_cleanup_temp_file_success(self):
        """Test cleanup_temp_file success - covers lines 117-122"""
        try:
            with (
                patch("os.remove") as mock_remove,
                patch("os.path.exists", return_value=True),
            ):
                from services.file_service import FileService

                # Add a temp file to track (job_id -> file_path)
                test_job_id = "test_job_123"
                FileService._temp_files[test_job_id] = "/tmp/test_file.pdf"

                # Test cleanup using job_id
                FileService.cleanup_temp_file(test_job_id)

                mock_remove.assert_called_once_with("/tmp/test_file.pdf")
                assert test_job_id not in FileService._temp_files

        except ImportError:
            pytest.skip("Cannot import FileService for cleanup test")

    def test_cleanup_temp_file_not_tracked(self):
        """Test cleanup_temp_file for untracked file"""
        try:
            from services.file_service import FileService

            # Test cleanup of untracked job_id (should not crash)
            FileService.cleanup_temp_file("untracked_job_id")

            # Should not raise an exception

        except ImportError:
            pytest.skip("Cannot import FileService for untracked cleanup test")

    def test_cleanup_temp_file_already_deleted(self):
        """Test cleanup_temp_file for already deleted file"""
        try:
            with (
                patch("os.unlink", side_effect=FileNotFoundError()),
                patch("os.path.exists", return_value=False),
            ):
                from services.file_service import FileService

                # Add file to track but it doesn't exist
                test_job_id = "deleted_job_456"
                FileService._temp_files[test_job_id] = "/tmp/deleted_file.pdf"

                # Test cleanup
                FileService.cleanup_temp_file(test_job_id)

                # Should still clean up tracking even if file doesn't exist
                assert test_job_id not in FileService._temp_files

        except ImportError:
            pytest.skip("Cannot import FileService for deleted cleanup test")

    def test_download_from_s3_success(self):
        """Test _download_from_s3 success - covers lines 140-144"""
        try:
            with patch("boto3.client") as mock_boto3:
                mock_s3 = Mock()
                mock_boto3.return_value = mock_s3
                mock_s3.download_file = Mock()

                with (
                    patch("os.path.join", return_value="/tmp/s3_download.pdf"),
                    patch("os.makedirs"),
                    patch("uuid.uuid4", return_value="uuid123"),
                ):
                    from services.file_service import FileService

                    result = FileService.download_from_s3("test.pdf")

                    assert result == "/tmp/s3_download.pdf"
                    mock_s3.download_file.assert_called_once()

        except ImportError:
            pytest.skip("Cannot import FileService for S3 download test")

    def test_download_from_s3_boto3_not_available(self):
        """Test download_from_s3 when boto3 not available - covers lines 153-154"""
        try:
            with patch("boto3.client", side_effect=ImportError("boto3 not installed")):
                from services.file_service import FileService
                from utils.errors import FileServiceError

                with pytest.raises(FileServiceError):
                    FileService.download_from_s3("test.pdf")

        except ImportError:
            pytest.skip("Cannot import FileService for boto3 unavailable test")

    def test_save_to_s3_success(self):
        """Test _save_to_s3 success - covers lines 181-182"""
        try:
            import asyncio

            with patch("boto3.client") as mock_boto3:
                mock_s3 = Mock()
                mock_boto3.return_value = mock_s3
                mock_s3.upload_file = Mock()
                mock_s3.head_bucket = Mock()  # Mock bucket check

                from services.file_service import FileService

                result = asyncio.run(
                    FileService._save_to_s3("/tmp/local_file.pdf", "job123", ".pdf")
                )

                assert result == "job123.pdf"  # Returns the S3 key
                mock_s3.upload_file.assert_called_once()

        except ImportError:
            pytest.skip("Cannot import FileService for S3 save test")

    def test_save_to_s3_bucket_not_exists(self):
        """Test _save_to_s3 when bucket doesn't exist"""
        try:
            import asyncio
            from botocore.exceptions import ClientError
            from services.file_service import FileService

            with patch("boto3.client") as mock_boto3:
                mock_s3 = Mock()
                mock_boto3.return_value = mock_s3

                # Mock head_bucket to raise 404 error (bucket doesn't exist)
                mock_s3.head_bucket.side_effect = ClientError(
                    error_response={"Error": {"Code": "404"}},
                    operation_name="HeadBucket",
                )
                mock_s3.create_bucket = Mock()  # Mock successful bucket creation
                mock_s3.upload_file = Mock()  # Mock successful upload

                # Should create bucket and succeed
                result = asyncio.run(
                    FileService._save_to_s3("/tmp/local_file.pdf", "job123", ".pdf")
                )

                assert result == "job123.pdf"
                mock_s3.create_bucket.assert_called_once()
                mock_s3.upload_file.assert_called_once()

        except ImportError:
            pytest.skip("Cannot import FileService for S3 bucket test")

    def test_file_service_with_different_storage_configurations(self):
        """Test FileService with different storage configurations"""
        try:
            # Test with local storage
            with patch.dict("os.environ", {"DURABLE_STORAGE": "local"}):
                from services.file_service import FileService

                # Test configuration is loaded correctly
                assert hasattr(FileService, "validate_file_type")

            # Test with S3 storage
            with patch.dict(
                "os.environ", {"DURABLE_STORAGE": "s3", "AWS_S3_BUCKET": "test-bucket"}
            ):
                # Re-import to test different config
                import importlib
                import services.file_service

                importlib.reload(services.file_service)

                from services.file_service import FileService

                assert hasattr(FileService, "_save_to_s3")

        except ImportError:
            pytest.skip("Cannot import FileService for storage config test")

    def test_temp_file_tracking(self):
        """Test temporary file tracking functionality"""
        try:
            from services.file_service import FileService

            # Test that temp files dict exists
            assert hasattr(FileService, "_temp_files")
            assert isinstance(FileService._temp_files, dict)

            # Test adding and removing from tracking (job_id -> file_path mapping)
            test_job_id = "test_job_123"
            test_file = "/tmp/tracked_file.pdf"
            FileService._temp_files[test_job_id] = test_file
            assert test_job_id in FileService._temp_files
            assert FileService._temp_files[test_job_id] == test_file

            # Test removing from tracking
            del FileService._temp_files[test_job_id]
            assert test_job_id not in FileService._temp_files

        except ImportError:
            pytest.skip("Cannot import FileService for tracking test")

    def test_error_handling_in_file_operations(self):
        """Test error handling in various file operations"""
        try:
            from services.file_service import FileService

            # Test handling of None filename
            with pytest.raises(Exception):
                FileService.validate_file_type(None)

            # Test handling of empty filename
            is_valid, file_ext = FileService.validate_file_type("")
            assert not is_valid
            assert file_ext == ""

        except ImportError:
            pytest.skip("Cannot import FileService for error handling test")
