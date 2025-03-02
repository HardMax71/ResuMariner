import logging
import os
from typing import Dict, Any

import httpx
from config import settings
from utils.errors import ProcessingServiceError

logger = logging.getLogger(__name__)


class ProcessingService:
    """Service for interacting with the CV processing service"""

    @staticmethod
    async def process_cv(file_path: str) -> Dict[str, Any]:
        """Send CV to processing service and return results"""
        try:
            # Ensure the file exists
            if not os.path.isfile(file_path):
                # Check if it's an S3 reference
                if file_path.startswith("s3:"):
                    from services.file_service import FileService
                    s3_key = file_path[3:]  # Remove "s3:" prefix
                    file_path = FileService.download_from_s3(s3_key)
                else:
                    raise ProcessingServiceError(f"File not found: {file_path}")

            # Send to processing service
            async with httpx.AsyncClient() as client:
                with open(file_path, "rb") as f:
                    files = {"file": (os.path.basename(file_path), f)}
                    response = await client.post(
                        f"{settings.PROCESSING_SERVICE_URL}/process",
                        files=files,
                        timeout=300.0  # 5 minutes timeout
                    )

            if response.status_code != 200:
                raise ProcessingServiceError(f"Processing error: {response.text}")

            # Return processing results
            result_data = response.json()

            logger.debug(
                f"Received from processing service: "
                f"{result_data.keys() if isinstance(result_data, dict) else 'not a dict'}")

            return result_data
        except httpx.RequestError as e:
            raise ProcessingServiceError(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}")
            raise ProcessingServiceError(f"Processing failed: {str(e)}")

    @staticmethod
    async def store_cv_data(job_id: str, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store processed CV data in storage service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.STORAGE_SERVICE_URL}/cv",
                    json={"job_id": job_id, "cv_data": cv_data}
                )

                if response.status_code != 200:
                    raise ProcessingServiceError(f"Storage error: {response.text}")

                return response.json()
        except httpx.RequestError as e:
            raise ProcessingServiceError(f"Storage request failed: {str(e)}")
        except Exception as e:
            raise ProcessingServiceError(f"Storage failed: {str(e)}")
