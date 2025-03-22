import logging
import os
import time
import uuid

import httpx
from config import settings
from fastapi import UploadFile, HTTPException
from models.processing_models import ProcessingResult, ProcessingOptions
from parsers.parse_image_service import ParseImageService
from parsers.parse_pdf_service import ParsePdfService
from pydantic import ValidationError
from services.content_structure_service import LLMContentStructureService
from services.embedding_service import EmbeddingService
from services.review_service import ReviewService
from utils.errors import BaseProcessingError, ParserError


class ProcessingService:
    """Main service for orchestrating CV processing"""

    def __init__(self):
        """Initialize processing service"""
        self.embedding_service = EmbeddingService(settings.EMBEDDING_MODEL)

    def _get_parser(self, file_path: str, file_ext: str):
        """Get appropriate parser for file type"""
        if file_ext == '.pdf':
            return ParsePdfService(file_path)
        elif file_ext in ['.jpg', '.jpeg', '.png']:
            return ParseImageService(file_path)
        else:
            raise ParserError(f"Unsupported file type: {file_ext}")

    async def process_file(self, file: UploadFile, file_path: str, options: ProcessingOptions) -> ProcessingResult:
        """Process a CV file

        Args:
            file: Uploaded file
            file_path: Path to saved file
            options: Processing options

        Returns:
            Processing result with structured data and review
        """
        start_time = time.time()
        metadata: dict[str, str | int] = {}
        cv_id = str(uuid.uuid4())  # Generate a unique ID for this CV

        try:
            # Determine file type
            if file.filename is None:
                raise ValueError("File name is missing")

            filename_parts = os.path.splitext(file.filename)
            if not filename_parts[1]:
                raise ValueError(f"Invalid file name or missing extension: {file.filename}")

            file_ext = filename_parts[1].lower()
            parser = self._get_parser(file_path, file_ext)

            # Parse document
            parsed_data = parser.parse_to_json()
            metadata["page_count"] = len(parsed_data.get("pages", []))
            logging.info(f"Parsed {metadata['page_count']} pages")

            # Structure content
            content_organizer = LLMContentStructureService(parsed_data)
            structured_data = await content_organizer.structure_content()
            logging.info("Structured CV data successfully")

            # Store structured data in database if requested
            if options.store_in_db:
                try:
                    async with httpx.AsyncClient() as client:
                        storage_response = await client.post(
                            f"{settings.STORAGE_SERVICE_URL}/cv",
                            json={"job_id": cv_id, "cv_data": structured_data.model_dump(mode="json",
                                                                                         exclude_none=True)},
                            timeout=60.0
                        )

                        if storage_response.status_code != 200:
                            logging.warning(f"Failed to store CV data: {storage_response.text}")
                        else:
                            logging.info(f"CV data stored with ID {cv_id}")
                            metadata["cv_id"] = cv_id

                            embeddings_stored = await self.embedding_service.send_embeddings_to_storage(
                                cv_id=cv_id,
                                resume=structured_data
                            )

                            if embeddings_stored:
                                logging.info(f"Embeddings stored successfully for CV {cv_id}")
                                metadata["embeddings_stored"] = True
                            else:
                                logging.warning(f"Failed to store embeddings for CV {cv_id}")
                                metadata["embeddings_stored"] = False
                            # We can still track successful storage of embeddings
                            result = storage_response.json()
                            metadata["embeddings_count"] = result.get("vector_count", 0)
                except Exception as e:
                    logging.error(f"Error storing data: {str(e)}")
                    metadata["storage_error"] = str(e)

            # Generate review if requested
            review_result = None
            if options.generate_review:
                review_service = ReviewService(parsed_data, structured_data)
                review_data = await review_service.iterative_review()
                review_result = review_data.model_dump(mode="json")
                logging.info("Generated CV review successfully")

            # Calculate processing time
            processing_time = time.time() - start_time
            metadata["processing_time_sec"] = int(processing_time)

            # Return the result without embeddings
            return ProcessingResult(
                structured_data=structured_data.model_dump(mode="json"),
                review=review_result,
                processing_time=processing_time,
                metadata=metadata
            )

        except ValidationError as e:
            logging.error(f"Validation error: {str(e)}")
            raise HTTPException(status_code=422, detail=f"Schema validation error: {str(e)}")
        except BaseProcessingError as e:
            logging.error(f"Processing error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
