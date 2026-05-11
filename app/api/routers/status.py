from fastapi import APIRouter, Depends
from app.schemas.status import HealthStatus
from app.core.settings import settings
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

router = APIRouter()

@router.get("/")
async def home_root():
    return {"message": "Welcome to the Dementia Tracker V1 API"}

@router.get("/health", response_model=HealthStatus)
async def health(db_session: AsyncSession = Depends(get_db)):
    try:
        result = await db_session.execute(text("SELECT 1"))
        return HealthStatus(
            status="ok",
            database="connected",
            version=settings.VERSION)
    except Exception as e:        
        return HealthStatus(
            status="error",
            database="unconnected",
            version=settings.VERSION
        )
	