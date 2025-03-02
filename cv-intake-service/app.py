import os

from config import settings
import logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
)
logger = logging.getLogger(__name__)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.cv_routes import router as cv_router

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
logger.info(f"Ensuring uploads directory exists at: {settings.UPLOAD_DIR}")

app = FastAPI(title="CV Intake Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cv_router, prefix="/api/v1", tags=["cv"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
