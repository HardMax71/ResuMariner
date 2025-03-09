import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routes.search_routes import router as search_router

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)
app = FastAPI(
    title=settings.SERVICE_NAME,
    description="CV Search Service"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router, tags=["search"])


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": settings.SERVICE_NAME,
        "embedding_model": settings.EMBEDDING_MODEL,
        "vector_size": settings.VECTOR_SIZE
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_config=None
    )
