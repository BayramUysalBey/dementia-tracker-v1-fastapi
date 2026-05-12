from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import  Depends
from app.db.session import get_db
from app.db.crud.reminder import ReminderCRUD
from app.db.models.reminder import Reminder
from app.schemas.reminder import ReminderCreate, ReminderUpdate
import uuid
from fastapi import HTTPException, status, Depends


class ReminderService:
    def __init__(
        self, 
        db: AsyncSession = Depends(get_db), 
        crud: ReminderCRUD = Depends(ReminderCRUD)
    ):
        self.db = db
        self.crud = crud
        
    async def create_reminder(self, create_in: ReminderCreate, user_id: uuid.UUID) -> Reminder:
        create_data = create_in.model_dump()
        create_data["user_id"] = user_id
        reminder = await self.crud.create_reminder(create_data)
        await self.db.refresh(reminder)
        return reminder
        
    async def get_all_reminder(self, user_id: uuid.UUID, skip: int = 0, limit: int = 1000) -> Sequence[Reminder]:
        return await self.crud.reminder_for_user(user_id=user_id, skip=skip, limit=limit)
    
    async def update_reminder(self, reminder_id: uuid.UUID, user_id: uuid.UUID, user_in: ReminderUpdate) -> Reminder:
        db_object = await self.crud.get_reminder_by_id(reminder_id)
        if not db_object or db_object.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
        update_data = user_in.model_dump(exclude_unset=True)
        updated_reminder = await self.crud.update_reminder(db_object, update_data)
        await self.db.refresh(updated_reminder)
        return updated_reminder