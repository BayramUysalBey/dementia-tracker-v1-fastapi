import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.db.models.note import Note
from app.db.session import get_db
from fastapi import Depends


class NoteCRUD:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
    
    async def create_note(self, obj_in: dict) -> Note:
        db_object = Note(**obj_in)
        self.db.add(db_object)
        await self.db.flush()
        return db_object

    async def note_for_user(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[Note]:
        result = await self.db.execute(
            select(Note)
            .where(or_(Note.author_id == user_id, Note.user_id == user_id)) # combine these two conditions with SQL OR" function
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def update_note(self, db_object: Note, obj_in: dict) -> Note:
        for field, value in obj_in.items():
            if hasattr(db_object, field):
                setattr(db_object, field, value)
        await self.db.flush()
        return db_object
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[Note]:
        result = await self.db.execute(select(Note).offset(skip).limit(limit))
        return result.scalars().all()
    
    async def get_note_by_id(self, note_id: uuid.UUID) -> Note | None:
        result = await self.db.execute(select(Note).where(Note.id == note_id))
        return result.scalars().first()