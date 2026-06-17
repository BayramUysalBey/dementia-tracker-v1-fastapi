import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.db.models.journal import Journal
from app.db.session import get_db
from fastapi import Depends


class JournalCRUD:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
    
    async def create_journal(self, obj_in: dict) -> Journal:
        db_object = Journal(**obj_in)
        self.db.add(db_object)
        await self.db.flush()
        return db_object

    async def journal_for_user(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[Journal]:
        result = await self.db.execute(
            select(Journal)
            .where(or_(Journal.author_id == user_id, Journal.user_id == user_id))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def update_journal(self, db_object: Journal, obj_in: dict) -> Journal:
        for field, value in obj_in.items():
            if hasattr(db_object, field):
                setattr(db_object, field, value)
        await self.db.flush()
        return db_object
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[Journal]:
        result = await self.db.execute(select(Journal).offset(skip).limit(limit))
        return result.scalars().all()
    
    async def get_journal_by_id(self, journal_id: uuid.UUID) -> Journal | None:
        result = await self.db.execute(select(Journal).where(Journal.id == journal_id))
        return result.scalars().first()
