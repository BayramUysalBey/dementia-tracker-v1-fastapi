from fastapi import FastAPI
from app.api.routers import status, items
from app.core.settings import settings

app = FastAPI(
    title="Dementia Tracker V1 API",
    description="Main API for Dementia Tracker",
    version=settings.VERSION
)

app.include_router(status.router)
app.include_router(items.router)
