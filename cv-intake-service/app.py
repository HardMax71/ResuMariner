import logging
import os

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from config import settings
from routes.cv_routes import router as cv_router
from utils.security import limiter, rate_limit_exceeded_handler
from utils.monitoring import init_monitoring, get_metrics, MetricsMiddleware
from utils.health_checks import health_checker

# Configure logging - use force=True to reconfigure if already set up
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    force=True,
)

logger = logging.getLogger(__name__)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
logger.info(f"Ensuring uploads directory exists at: {settings.UPLOAD_DIR}")

app = FastAPI(
    title="CV Intake Service",
    description="Service for uploading and managing CV processing jobs",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Initialize monitoring
init_monitoring(app, "cv-intake-service")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)  # type: ignore[arg-type]

# Add metrics middleware
app.add_middleware(MetricsMiddleware, service_name="cv-intake-service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cv_router, prefix="/api/v1", tags=["cv"])


@app.get("/queue-stats")
async def get_queue_stats():
    """Get Redis queue statistics"""
    try:
        from utils.redis_queue import redis_queue

        stats = redis_queue.get_queue_stats()
        return {"status": "ok", "queue_stats": stats}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=get_metrics(), media_type="text/plain")


@app.get("/health")
async def health_check():
    """Basic health check"""
    from datetime import datetime

    return {
        "status": "ok",
        "service": "cv-intake-service",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health/detailed")
async def detailed_health_check(response: Response):
    """Comprehensive health check"""
    health_result = await health_checker.get_comprehensive_health()

    # Debug: log the health_result status for test debugging
    logger.debug(f"Health check result status: {health_result.get('status')}")

    # Set HTTP status code based on health status
    if health_result.get("status") == "healthy":
        response.status_code = status.HTTP_200_OK
    elif health_result.get("status") in ["warning"]:
        response.status_code = status.HTTP_200_OK  # Warning is still OK
    else:  # unhealthy, critical, or any other status
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return health_result


@app.get("/health/ready")
async def readiness_check(response: Response):
    """Readiness check"""
    readiness_result = await health_checker.get_readiness_check()

    # Set HTTP status code based on readiness
    if readiness_result.get("ready"):
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return readiness_result


@app.get("/health/live")
async def liveness_check(response: Response):
    """Liveness check"""
    liveness_result = await health_checker.get_liveness_check()

    # Set HTTP status code based on liveness
    if liveness_result.get("alive"):
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return liveness_result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app", host="0.0.0.0", port=8000, reload=settings.DEBUG, log_config=None
    )
