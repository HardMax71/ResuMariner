import logging

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routes.processing_routes import router as processing_router
from utils.monitoring import init_monitoring, get_metrics, MetricsMiddleware

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)

app = FastAPI(title="CV Processing Service")

# Initialize monitoring
init_monitoring(app, "cv-processing-service")

# Add metrics middleware
app.add_middleware(MetricsMiddleware, service_name="cv-processing-service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(processing_router, tags=["processing"])


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=get_metrics(), media_type="text/plain")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "cv-processing-service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app", host="0.0.0.0", port=8001, reload=settings.DEBUG, log_config=None
    )
