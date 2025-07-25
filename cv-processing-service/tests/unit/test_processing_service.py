"""Comprehensive tests for cv-processing-service ProcessingService to achieve 95%+ coverage."""

import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import UploadFile, HTTPException

# Mock environment variables before any imports that use config
with patch.dict(os.environ, {"LLM_API_KEY": "test-api-key-123"}, clear=False):
    from services.processing_service import ProcessingService
    from models.processing_models import ProcessingOptions, ProcessingResult
    from utils.errors import BaseProcessingError, ParserError


class TestProcessingService:
    """Test ProcessingService functionality"""

    @pytest.fixture
    def processing_service(self):
        """Create ProcessingService instance"""
        with patch("services.processing_service.EmbeddingService"):
            return ProcessingService()

    @pytest.fixture
    def mock_upload_file(self):
        """Create mock UploadFile"""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.pdf"
        mock_file.content_type = "application/pdf"
        return mock_file

    @pytest.fixture
    def processing_options(self):
        """Create ProcessingOptions"""
        return ProcessingOptions(parallel=False, generate_review=True, store_in_db=True)

    def test_processing_service_initialization(self, processing_service):
        """Test ProcessingService initialization"""
        assert processing_service is not None
        assert hasattr(processing_service, "embedding_service")

    def test_get_parser_pdf(self, processing_service):
        """Test _get_parser with PDF file"""
        with patch("services.processing_service.ParsePdfService") as mock_parser:
            parser = processing_service._get_parser("/path/test.pdf", ".pdf")

            mock_parser.assert_called_once_with("/path/test.pdf")
            assert parser is not None

    def test_get_parser_image_jpg(self, processing_service):
        """Test _get_parser with JPG file"""
        with patch("services.processing_service.ParseImageService") as mock_parser:
            parser = processing_service._get_parser("/path/test.jpg", ".jpg")

            mock_parser.assert_called_once_with("/path/test.jpg")
            assert parser is not None

    def test_get_parser_image_jpeg(self, processing_service):
        """Test _get_parser with JPEG file"""
        with patch("services.processing_service.ParseImageService") as mock_parser:
            parser = processing_service._get_parser("/path/test.jpeg", ".jpeg")

            mock_parser.assert_called_once_with("/path/test.jpeg")
            assert parser is not None

    def test_get_parser_image_png(self, processing_service):
        """Test _get_parser with PNG file"""
        with patch("services.processing_service.ParseImageService") as mock_parser:
            parser = processing_service._get_parser("/path/test.png", ".png")

            mock_parser.assert_called_once_with("/path/test.png")
            assert parser is not None

    def test_get_parser_unsupported_file_type(self, processing_service):
        """Test _get_parser with unsupported file type"""
        with pytest.raises(ParserError) as exc_info:
            processing_service._get_parser("/path/test.docx", ".docx")

        assert "Unsupported file type: .docx" in str(exc_info.value)

    @patch("services.processing_service.LLMContentStructureService")
    @patch("services.processing_service.ReviewService")
    @patch("services.processing_service.ParsePdfService")
    @patch("services.processing_service.time.time")
    @patch("services.processing_service.uuid.uuid4")
    @patch("services.processing_service.httpx.AsyncClient")
    @pytest.mark.asyncio
    async def test_process_file_success_pdf(
        self,
        mock_httpx,
        mock_uuid,
        mock_time,
        mock_pdf_parser,
        mock_review_service,
        mock_structure_service,
        processing_service,
        mock_upload_file,
        processing_options,
    ):
        """Test successful file processing with PDF"""
        # Setup mocks
        mock_uuid.return_value = MagicMock()
        mock_uuid.return_value.__str__ = MagicMock(return_value="test-cv-id-123")
        mock_time.side_effect = [0.0, 10.0]  # start and end times

        # Mock parser
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = "Extracted text content"
        mock_pdf_parser.return_value = mock_parser_instance

        # Mock structure service
        mock_structure_instance = MagicMock()
        mock_structure_instance.extract_structure = AsyncMock(
            return_value={"name": "John Doe", "skills": ["Python", "FastAPI"]}
        )
        mock_structure_service.return_value = mock_structure_instance

        # Mock review service
        mock_review_instance = MagicMock()
        mock_review_instance.generate_review = AsyncMock(
            return_value={"score": 85, "feedback": "Good candidate"}
        )
        mock_review_service.return_value = mock_review_instance

        # Mock storage service call
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "stored", "cv_id": "stored-cv-id"}
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_httpx.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_httpx.return_value.__aexit__ = AsyncMock()

        result = await processing_service.process_file(
            mock_upload_file, "/tmp/test.pdf", processing_options
        )

        assert isinstance(result, ProcessingResult)
        assert result.structured_data["name"] == "John Doe"
        assert result.review["score"] == 85
        assert result.processing_time == 10.0
        assert result.metadata["cv_id"] == "test-cv-id-123"

    @patch("services.processing_service.ParseImageService")
    @patch("services.processing_service.LLMContentStructureService")
    @patch("services.processing_service.time.time")
    @patch("services.processing_service.uuid.uuid4")
    @pytest.mark.asyncio
    async def test_process_file_success_image_no_review(
        self,
        mock_uuid,
        mock_time,
        mock_structure_service,
        mock_image_parser,
        processing_service,
        mock_upload_file,
    ):
        """Test successful file processing with image and no review"""
        # Setup file as image
        mock_upload_file.filename = "test.jpg"

        # Setup mocks
        mock_uuid.return_value = MagicMock()
        mock_uuid.return_value.__str__ = MagicMock(return_value="test-cv-id-456")
        mock_time.side_effect = [0.0, 5.0]

        # Mock parser
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = "Extracted image text"
        mock_image_parser.return_value = mock_parser_instance

        # Mock structure service
        mock_structure_instance = MagicMock()
        mock_structure_instance.extract_structure = AsyncMock(
            return_value={"name": "Jane Smith", "skills": ["Java"]}
        )
        mock_structure_service.return_value = mock_structure_instance

        # No review option
        options = ProcessingOptions(
            parallel=False, generate_review=False, store_in_db=False
        )

        result = await processing_service.process_file(
            mock_upload_file, "/tmp/test.jpg", options
        )

        assert isinstance(result, ProcessingResult)
        assert result.structured_data["name"] == "Jane Smith"
        assert result.review is None
        assert result.processing_time == 5.0

    @patch("services.processing_service.ParsePdfService")
    @pytest.mark.asyncio
    async def test_process_file_parser_error(
        self, mock_pdf_parser, processing_service, mock_upload_file, processing_options
    ):
        """Test file processing with parser error"""
        # Mock parser to raise error
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.side_effect = ParserError("Failed to parse PDF")
        mock_pdf_parser.return_value = mock_parser_instance

        with pytest.raises(HTTPException) as exc_info:
            await processing_service.process_file(
                mock_upload_file, "/tmp/test.pdf", processing_options
            )

        assert exc_info.value.status_code == 400
        assert "Failed to parse PDF" in exc_info.value.detail

    @patch("services.processing_service.ParsePdfService")
    @patch("services.processing_service.LLMContentStructureService")
    @pytest.mark.asyncio
    async def test_process_file_structure_service_error(
        self,
        mock_structure_service,
        mock_pdf_parser,
        processing_service,
        mock_upload_file,
        processing_options,
    ):
        """Test file processing with structure service error"""
        # Mock parser success
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = "Text content"
        mock_pdf_parser.return_value = mock_parser_instance

        # Mock structure service error
        mock_structure_instance = MagicMock()
        mock_structure_instance.extract_structure = AsyncMock(
            side_effect=BaseProcessingError("Structure extraction failed")
        )
        mock_structure_service.return_value = mock_structure_instance

        with pytest.raises(HTTPException) as exc_info:
            await processing_service.process_file(
                mock_upload_file, "/tmp/test.pdf", processing_options
            )

        assert exc_info.value.status_code == 500
        assert "Structure extraction failed" in exc_info.value.detail

    @patch("services.processing_service.ParsePdfService")
    @patch("services.processing_service.LLMContentStructureService")
    @patch("services.processing_service.ReviewService")
    @pytest.mark.asyncio
    async def test_process_file_review_service_error(
        self,
        mock_review_service,
        mock_structure_service,
        mock_pdf_parser,
        processing_service,
        mock_upload_file,
        processing_options,
    ):
        """Test file processing with review service error"""
        # Mock parser success
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = "Text content"
        mock_pdf_parser.return_value = mock_parser_instance

        # Mock structure service success
        mock_structure_instance = MagicMock()
        mock_structure_instance.extract_structure = AsyncMock(
            return_value={"name": "Test User"}
        )
        mock_structure_service.return_value = mock_structure_instance

        # Mock review service error
        mock_review_instance = MagicMock()
        mock_review_instance.generate_review = AsyncMock(
            side_effect=BaseProcessingError("Review generation failed")
        )
        mock_review_service.return_value = mock_review_instance

        with pytest.raises(HTTPException) as exc_info:
            await processing_service.process_file(
                mock_upload_file, "/tmp/test.pdf", processing_options
            )

        assert exc_info.value.status_code == 500
        assert "Review generation failed" in exc_info.value.detail

    @patch("services.processing_service.ParsePdfService")
    @patch("services.processing_service.LLMContentStructureService")
    @patch("services.processing_service.httpx.AsyncClient")
    @pytest.mark.asyncio
    async def test_process_file_storage_service_error(
        self,
        mock_httpx,
        mock_structure_service,
        mock_pdf_parser,
        processing_service,
        mock_upload_file,
        processing_options,
    ):
        """Test file processing with storage service error"""
        # Mock parser success
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = "Text content"
        mock_pdf_parser.return_value = mock_parser_instance

        # Mock structure service success
        mock_structure_instance = MagicMock()
        mock_structure_instance.extract_structure = AsyncMock(
            return_value={"name": "Test User"}
        )
        mock_structure_service.return_value = mock_structure_instance

        # Mock storage service error
        mock_client = MagicMock()
        mock_client.post = AsyncMock(side_effect=Exception("Storage service down"))
        mock_httpx.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_httpx.return_value.__aexit__ = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await processing_service.process_file(
                mock_upload_file, "/tmp/test.pdf", processing_options
            )

        assert exc_info.value.status_code == 500
        assert "Storage service down" in exc_info.value.detail

    @patch("services.processing_service.ParsePdfService")
    @patch("services.processing_service.LLMContentStructureService")
    @patch("services.processing_service.ReviewService")
    @patch("services.processing_service.httpx.AsyncClient")
    @patch("services.processing_service.time.time")
    @patch("services.processing_service.uuid.uuid4")
    @pytest.mark.asyncio
    async def test_process_file_parallel_processing(
        self,
        mock_uuid,
        mock_time,
        mock_httpx,
        mock_review_service,
        mock_structure_service,
        mock_pdf_parser,
        processing_service,
        mock_upload_file,
    ):
        """Test file processing with parallel processing enabled"""
        # Setup mocks
        mock_uuid.return_value = MagicMock()
        mock_uuid.return_value.__str__ = MagicMock(return_value="parallel-cv-id")
        mock_time.side_effect = [0.0, 8.0]

        # Mock all services
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = "Content"
        mock_pdf_parser.return_value = mock_parser_instance

        mock_structure_instance = MagicMock()
        mock_structure_instance.extract_structure = AsyncMock(
            return_value={"name": "Parallel User"}
        )
        mock_structure_service.return_value = mock_structure_instance

        mock_review_instance = MagicMock()
        mock_review_instance.generate_review = AsyncMock(return_value={"score": 90})
        mock_review_service.return_value = mock_review_instance

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "stored"}
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_httpx.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_httpx.return_value.__aexit__ = AsyncMock()

        # Enable parallel processing
        options = ProcessingOptions(
            parallel=True, generate_review=True, store_in_db=True
        )

        result = await processing_service.process_file(
            mock_upload_file, "/tmp/test.pdf", options
        )

        assert result.structured_data["name"] == "Parallel User"
        assert result.review["score"] == 90
        assert result.metadata["cv_id"] == "parallel-cv-id"

    @patch("services.processing_service.ParsePdfService")
    @pytest.mark.asyncio
    async def test_process_file_unsupported_file_extension(
        self, mock_pdf_parser, processing_service, processing_options
    ):
        """Test processing file with unsupported extension"""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.docx"

        with pytest.raises(HTTPException) as exc_info:
            await processing_service.process_file(
                mock_file, "/tmp/test.docx", processing_options
            )

        assert exc_info.value.status_code == 400
        assert "Unsupported file type" in exc_info.value.detail

    @patch("services.processing_service.ParsePdfService")
    @patch("services.processing_service.LLMContentStructureService")
    @patch("services.processing_service.httpx.AsyncClient")
    @patch("services.processing_service.time.time")
    @patch("services.processing_service.uuid.uuid4")
    @pytest.mark.asyncio
    async def test_process_file_storage_disabled(
        self,
        mock_uuid,
        mock_time,
        mock_httpx,
        mock_structure_service,
        mock_pdf_parser,
        processing_service,
        mock_upload_file,
    ):
        """Test file processing with storage disabled"""
        # Setup mocks
        mock_uuid.return_value = MagicMock()
        mock_uuid.return_value.__str__ = MagicMock(return_value="no-storage-cv-id")
        mock_time.side_effect = [0.0, 3.0]

        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = "Content"
        mock_pdf_parser.return_value = mock_parser_instance

        mock_structure_instance = MagicMock()
        mock_structure_instance.extract_structure = AsyncMock(
            return_value={"name": "No Storage User"}
        )
        mock_structure_service.return_value = mock_structure_instance

        # Disable storage
        options = ProcessingOptions(
            parallel=False, generate_review=False, store_in_db=False
        )

        result = await processing_service.process_file(
            mock_upload_file, "/tmp/test.pdf", options
        )

        # Storage service should not be called
        mock_httpx.assert_not_called()

        assert result.structured_data["name"] == "No Storage User"
        assert result.review is None

    @patch("services.processing_service.os.path.splitext")
    @pytest.mark.asyncio
    async def test_process_file_extension_extraction(
        self, mock_splitext, processing_service, mock_upload_file, processing_options
    ):
        """Test file extension extraction"""
        mock_splitext.return_value = ("test", ".pdf")

        with patch.object(processing_service, "_get_parser") as mock_get_parser:
            mock_parser = MagicMock()
            mock_parser.parse.return_value = "Content"
            mock_get_parser.return_value = mock_parser

            with patch(
                "services.processing_service.LLMContentStructureService"
            ) as mock_service:
                mock_instance = MagicMock()
                mock_instance.extract_structure = AsyncMock(
                    return_value={"name": "Test"}
                )
                mock_service.return_value = mock_instance

                await processing_service.process_file(
                    mock_upload_file, "/tmp/test.pdf", processing_options
                )

                mock_splitext.assert_called_once_with("/tmp/test.pdf")
                mock_get_parser.assert_called_once_with("/tmp/test.pdf", ".pdf")

    def test_embedding_service_initialization(self):
        """Test embedding service is initialized correctly"""
        with patch("services.processing_service.EmbeddingService") as mock_embedding:
            with patch("config.settings") as mock_settings:
                mock_settings.EMBEDDING_MODEL = "test-embedding-model"

                service = ProcessingService()

                mock_embedding.assert_called_once_with("test-embedding-model")
                assert service.embedding_service is not None

    @pytest.mark.asyncio
    async def test_process_file_generic_exception(
        self, processing_service, mock_upload_file, processing_options
    ):
        """Test handling of generic exceptions"""
        with patch.object(processing_service, "_get_parser") as mock_get_parser:
            mock_get_parser.side_effect = Exception("Unexpected error")

            with pytest.raises(HTTPException) as exc_info:
                await processing_service.process_file(
                    mock_upload_file, "/tmp/test.pdf", processing_options
                )

            assert exc_info.value.status_code == 500
            assert "Unexpected error" in exc_info.value.detail
