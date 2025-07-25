import os
import time
from typing import Dict, Any

import httpx
from config import settings
from utils.errors import ProcessingServiceError
from utils.circuit_breaker import CircuitBreaker, resilient_http_call
from utils.logger import ServiceLogger, set_request_context

logger = ServiceLogger(__name__)

# Circuit breakers for different services
processing_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
storage_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60)


class ProcessingService:
    """Service for interacting with the CV processing service"""

    @staticmethod
    async def process_cv(file_path: str, job_id: str = None) -> Dict[str, Any]:
        """Send CV to processing service and return results"""
        start_time = time.time()

        # Set logging context
        set_request_context(
            job_id=job_id, file_name=os.path.basename(file_path) if file_path else None
        )

        try:
            # Ensure the file exists
            if not os.path.isfile(file_path):
                # Check if it's an S3 reference
                if file_path.startswith("s3:"):
                    from services.file_service import FileService

                    s3_key = file_path[3:]  # Remove "s3:" prefix
                    file_path = FileService.download_from_s3(s3_key)
                else:
                    raise ProcessingServiceError(
                        f"File not found: {file_path}",
                        error_code="FILE_NOT_FOUND",
                        details={"file_path": file_path},
                    )

            # Use circuit breaker for processing service call
            async def make_processing_call():
                async with httpx.AsyncClient(timeout=300.0) as client:
                    with open(file_path, "rb") as f:
                        files = {"file": (os.path.basename(file_path), f)}
                        return await resilient_http_call(
                            client,
                            "POST",
                            f"{settings.PROCESSING_SERVICE_URL}/process",
                            files=files,
                        )

            response = await processing_circuit_breaker.call(make_processing_call)

            # Process successful response
            result_data = response.json()
            duration_ms = int((time.time() - start_time) * 1000)

            logger.service_call(
                "cv-processing-service",
                "process",
                "success",
                duration_ms=duration_ms,
                file_size=os.path.getsize(file_path)
                if os.path.isfile(file_path)
                else None,
            )

            return result_data

        except httpx.TimeoutException as _:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.service_call(
                "cv-processing-service", "process", "timeout", duration_ms=duration_ms
            )
            raise ProcessingServiceError(
                "Processing service timeout",
                error_code="PROCESSING_TIMEOUT",
                details={"timeout_seconds": 300, "file_path": file_path},
            )
        except httpx.HTTPStatusError as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.service_call(
                "cv-processing-service",
                "process",
                "http_error",
                duration_ms=duration_ms,
                status_code=e.response.status_code,
            )
            raise ProcessingServiceError(
                f"Processing service error: {e.response.status_code}",
                error_code="PROCESSING_HTTP_ERROR",
                status_code=e.response.status_code,
                response_text=e.response.text,
            )
        except httpx.RequestError as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.service_call(
                "cv-processing-service",
                "process",
                "request_error",
                duration_ms=duration_ms,
            )
            raise ProcessingServiceError(
                f"Request failed: {str(e)}",
                error_code="PROCESSING_REQUEST_ERROR",
                details={"original_error": str(e)},
            )
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(
                f"Processing failed: {str(e)}",
                error=e,
                duration_ms=duration_ms,
                file_path=file_path,
            )
            raise ProcessingServiceError(
                f"Processing failed: {str(e)}",
                error_code="PROCESSING_UNEXPECTED_ERROR",
                details={"original_error": str(e)},
            )

    @staticmethod
    async def store_cv_data(job_id: str, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store processed CV data in storage service"""
        start_time = time.time()

        # Set logging context
        set_request_context(job_id=job_id)

        try:
            # Use circuit breaker for storage service call
            async def make_storage_call():
                async with httpx.AsyncClient(timeout=60.0) as client:
                    return await resilient_http_call(
                        client,
                        "POST",
                        f"{settings.STORAGE_SERVICE_URL}/cv",
                        json={"job_id": job_id, "cv_data": cv_data},
                    )

            response = await storage_circuit_breaker.call(make_storage_call)

            # Process successful response
            result_data = response.json()
            duration_ms = int((time.time() - start_time) * 1000)

            logger.service_call(
                "cv-storage-service",
                "store",
                "success",
                duration_ms=duration_ms,
                data_size=len(str(cv_data)),
            )

            return result_data

        except httpx.TimeoutException as _:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.service_call(
                "cv-storage-service", "store", "timeout", duration_ms=duration_ms
            )
            raise ProcessingServiceError(
                "Storage service timeout",
                error_code="STORAGE_TIMEOUT",
                details={"timeout_seconds": 60, "job_id": job_id},
            )
        except httpx.HTTPStatusError as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.service_call(
                "cv-storage-service",
                "store",
                "http_error",
                duration_ms=duration_ms,
                status_code=e.response.status_code,
            )
            raise ProcessingServiceError(
                f"Storage service error: {e.response.status_code}",
                error_code="STORAGE_HTTP_ERROR",
                status_code=e.response.status_code,
                response_text=e.response.text,
            )
        except httpx.RequestError as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.service_call(
                "cv-storage-service", "store", "request_error", duration_ms=duration_ms
            )
            raise ProcessingServiceError(
                f"Storage request failed: {str(e)}",
                error_code="STORAGE_REQUEST_ERROR",
                details={"original_error": str(e)},
            )
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(
                f"Storage failed: {str(e)}",
                error=e,
                duration_ms=duration_ms,
                job_id=job_id,
            )
            raise ProcessingServiceError(
                f"Storage failed: {str(e)}",
                error_code="STORAGE_UNEXPECTED_ERROR",
                details={"original_error": str(e)},
            )
