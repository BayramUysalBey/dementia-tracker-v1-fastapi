import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.emergency_contact import EmergencyContact
from app.db.session import get_db
from fastapi import Depends


class EmergencyContactsCRUD:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
    
    async def create_emergency_contacts(self, obj_in: dict) -> EmergencyContact:
        db_object = EmergencyContact(**obj_in)
        self.db.add(db_object)
        await self.db.flush()
        return db_object

    async def emergency_contacts_for_user(self, user_id: uuid.UUID) -> Sequence[EmergencyContact]:
        result = await self.db.execute(select(EmergencyContact).where(EmergencyContact.user_id == user_id))
        return result.scalars().all()

    async def update_emergency_contacts(self, db_object: EmergencyContact, obj_in: dict) -> EmergencyContact:
        for field, value in obj_in.items():
            if hasattr(db_object, field):
                setattr(db_object, field, value)
        return db_object
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[EmergencyContact]:
        result = await self.db.execute(select(EmergencyContact).offset(skip).limit(limit))
        return result.scalars().all()