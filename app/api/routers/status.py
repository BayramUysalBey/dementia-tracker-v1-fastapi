from fastapi import APIRouter
from app.schemas.status import HealthStatus
from app.core.settings import settings

router = APIRouter()

@router.get("/")
async def home_root():
    return {"message": "Welcome to the Dementia Tracker V1 API"}

@router.get("/health", response_model=HealthStatus)
async def health():
    return HealthStatus(
        status="up",
        database="disconnected",
        version=settings.VERSION
    )
