import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.media import Media
from app.db.session import get_db
from fastapi import Depends


class MediaCRUD:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
    
    async def create_media(self, obj_in: dict) -> Media:
        db_object = Media(**obj_in)
        self.db.add(db_object)
        await self.db.flush()
        return db_object

    async def media_for_user(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[Media]:
        result = await self.db.execute(select(Media).where(Media.user_id == user_id).offset(skip).limit(limit))
        return result.scalars().all()

    async def update_media(self, db_object: Media, obj_in: dict) -> Media:
        for field, value in obj_in.items():
            if hasattr(db_object, field):
                setattr(db_object, field, value)
                await self.db.flush()
        return db_object
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[Media]:
        result = await self.db.execute(select(Media).offset(skip).limit(limit))
        return result.scalars().all()
    
    async def get_media_by_id(self, media_id: uuid.UUID) -> Media | None:
        result = await self.db.execute(select(Media).where(Media.id == media_id))
        return result.scalars().first()