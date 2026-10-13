import logging
from fastapi import APIRouter, Depends
from app.schemas.status import HealthStatus
from app.core.settings import settings
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import Response, status as http_status


router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
async def home_root():
    return {"message": "Welcome to the Dementia Tracker V1 API"}


@router.get("/health", response_model=HealthStatus,
            responses={503: {"model": HealthStatus,
                             "description": "Database unreachable"}})
async def health(response: Response, db_session: AsyncSession = Depends(get_db)):
    try:
        await db_session.execute(text("SELECT 1"))
        return HealthStatus(status="ok", database="connected", version=settings.VERSION)
    except SQLAlchemyError as s_e:
        logger.error(f"Database health check failed: {s_e}", exc_info=True)
        response.status_code = http_status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthStatus(status="error", database="unconnected", version=settings.VERSION)
    except Exception as e:
        logger.error(f"Unexpected error during health check: {e}", exc_info=True)
        response.status_code = http_status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthStatus(status="error", database="unconnected", version=settings.VERSION)