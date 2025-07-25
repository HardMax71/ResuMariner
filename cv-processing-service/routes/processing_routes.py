import logging
import os
import tempfile

from config import settings
from fastapi import File, UploadFile, Form, HTTPException, APIRouter
from models.processing_models import ProcessingResult, ProcessingOptions
from services.processing_service import ProcessingService

logger = logging.getLogger(__name__)
processing_service = ProcessingService()
router = APIRouter()


@router.post("/process", response_model=ProcessingResult)
async def process_cv(
    file: UploadFile = File(...),
    parallel: bool = Form(False),
    generate_review: bool = Form(True),
    store_in_db: bool = Form(True),
):
    """Process a CV file and return structured data

    Args:
        file: CV file (PDF, JPG, PNG)
        parallel: Whether to use parallel processing
        generate_review: Whether to generate a CV review
        store_in_db: Whether to store processed data in DB

    Returns:
        Structured CV data, review, and embeddings (if requested)
    """
    # Create temp file
    if file.filename is None:
        raise ValueError("File name is missing")
    temp_file = tempfile.NamedTemporaryFile(
        delete=False, suffix=os.path.splitext(file.filename)[1]
    )

    try:
        # Save uploaded file to temp file
        content = await file.read()
        temp_file.write(content)
        temp_file.close()

        # Create options object
        options = ProcessingOptions(
            parallel=parallel, generate_review=generate_review, store_in_db=store_in_db
        )

        # Process the file
        result = await processing_service.process_file(file, temp_file.name, options)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    finally:
        # Clean up temp file
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL,
    }
