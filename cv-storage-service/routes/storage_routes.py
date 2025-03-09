import logging

from config import settings
from fastapi import HTTPException, APIRouter
from models.storage_models import (
    StoreRequest, StoreResponse,
    VectorStoreRequest, VectorStoreResponse
)
from services.graph_db_service import GraphDBService
from services.vector_db_service import VectorDBService
from utils.errors import StorageServiceError, GraphDBError, VectorDBError, DatabaseConnectionError

logger = logging.getLogger(__name__)

try:
    graph_db = GraphDBService(
        uri=settings.NEO4J_URI,
        username=settings.NEO4J_USER,
        password=settings.NEO4J_PASSWORD
    )

    vector_db = VectorDBService(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
        collection_name=settings.QDRANT_COLLECTION,
        vector_size=settings.VECTOR_SIZE
    )

    logger.info("Database services initialized successfully")
except DatabaseConnectionError as e:
    logger.error(f"Database connection error: {str(e)}")
    raise
except Exception as e:
    logger.error(f"Unexpected error during initialization: {str(e)}")
    raise

router = APIRouter()


@router.post("/cv", response_model=StoreResponse)
async def store_cv(request: StoreRequest):
    """Store CV data in the graph database

    The CV data must contain structured information following the resume schema.
    Checks for duplicates based on email and overwrites existing data if found.
    """
    try:
        # Extract identifying information for logging purposes
        personal_info = request.cv_data.get("personal_info", {})
        email = personal_info.get("contact", {}).get("email", "unknown")

        # Check if this person already exists (for logging only)
        is_update = False
        if email != "unknown":
            existing_person = graph_db.find_existing_person(email)
            is_update = existing_person is not None and len(existing_person.get("cv_ids", [])) > 0

        # Store in graph database (will handle duplicate detection internally)
        graph_id = graph_db.store_cv(request.cv_data, request.job_id)

        # Log appropriate message
        if is_update:
            logger.info(f"Updated existing CV for {email} in graph database with ID: {graph_id}")
        else:
            logger.info(f"Stored new CV in graph database with ID: {graph_id}")

        return StoreResponse(
            graph_id=graph_id,
            vector_count=0  # No vectors stored initially
        )
    except GraphDBError as e:
        logger.error(f"Graph database error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Graph database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Storage operation failed: {str(e)}")


@router.get("/cv/{cv_id}")
async def get_cv(cv_id: str):
    """Retrieve CV data from graph database"""
    try:
        # Get CV details
        cv_details = graph_db.get_cv_details([cv_id])

        if not cv_details or cv_id not in cv_details:
            raise HTTPException(status_code=404, detail=f"CV with ID {cv_id} not found")

        return cv_details[cv_id]
    except GraphDBError as e:
        logger.error(f"Graph database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Graph database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Retrieval operation failed: {str(e)}")


@router.post("/vectors", response_model=VectorStoreResponse)
async def store_vectors(request: VectorStoreRequest):
    """Store pre-computed vectors in vector database

    This endpoint expects pre-computed vectors with associated metadata.
    Will delete any existing vectors for the same CV before storing new ones.
    """
    try:
        cv_id = request.cv_id
        vectors = request.vectors

        logger.info(f"Received {len(vectors)} vectors to store for CV {cv_id}")

        # Convert to required format for vector_db service
        formatted_vectors = [
            {
                "vector": v.vector,
                "text": v.text,
                "person_name": v.person_name,
                "email": v.email,
                "source": v.source,
                "context": v.context or ""
            }
            for v in vectors
        ]

        # store_vectors method now handles deletion of existing vectors
        vector_ids = vector_db.store_vectors(cv_id, formatted_vectors)
        logger.info(f"Stored {len(vector_ids)} vectors for CV {cv_id}")

        return VectorStoreResponse(
            status="success",
            vector_count=len(vector_ids)
        )
    except VectorDBError as e:
        logger.error(f"Vector database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Vector database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Vector storage failed: {str(e)}")


@router.delete("/cv/{cv_id}")
async def delete_cv(cv_id: str):
    """Delete a CV and all related data from both databases"""
    try:
        # Delete from graph database
        graph_db.delete_cv(cv_id)
        logger.info(f"Deleted CV {cv_id} from graph database")

        # Delete from vector database
        vector_count = vector_db.delete_cv_vectors(cv_id)
        logger.info(f"Deleted {vector_count} vectors for CV {cv_id} from vector database")

        return {"status": "success", "message": f"CV {cv_id} deleted successfully"}
    except StorageServiceError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete operation failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": settings.SERVICE_NAME,
        "graph_db": "connected",
        "vector_db": "connected"
    }
