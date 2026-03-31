from fastapi import FastAPI
from app.api.routers import api_router
from app.core.settings import settings

app = FastAPI(
    title="Dementia Tracker V1 API",
    description="Main API for Dementia Tracker",
    version=settings.VERSION
)

app.include_router(api_router, prefix="/api")
