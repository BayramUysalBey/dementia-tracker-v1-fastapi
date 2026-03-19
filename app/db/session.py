import asyncio
from typing import AsyncGenerator
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.settings import settings
import logging

logger = logging.getLogger(__name__)



meta = MetaData()
engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

			
async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(e, exc_info=e)
            raise e
        else:
            await session.commit()
        finally:
            await session.close()