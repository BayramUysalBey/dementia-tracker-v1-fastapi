import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.reminder import Reminder
from app.db.session import get_db
from fastapi import Depends


class ReminderCRUD:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
    
    async def create_reminder(self, obj_in: dict) -> Reminder:
        db_object = Reminder(**obj_in)
        self.db.add(db_object)
        await self.db.flush()
        return db_object

    async def reminder_for_user(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[Reminder]:
        result = await self.db.execute(select(Reminder).where(Reminder.user_id == user_id).offset(skip).limit(limit))
        return result.scalars().all()

    async def update_reminder(self, db_object: Reminder, obj_in: dict) -> Reminder:
        for field, value in obj_in.items():
            if hasattr(db_object, field):
                setattr(db_object, field, value)
        await self.db.flush()
        return db_object
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[Reminder]:
        result = await self.db.execute(select(Reminder).offset(skip).limit(limit))
        return result.scalars().all()
    
    async def get_reminder_by_id(self, reminder_id: uuid.UUID) -> Reminder | None:
        result = await self.db.execute(select(Reminder).where(Reminder.id == reminder_id))
        return result.scalars().first()