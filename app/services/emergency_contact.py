from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import  Depends
from app.db.session import get_db
from app.db.crud.emergency_contact import EmergencyContactsCRUD
from app.db.models.emergency_contact import EmergencyContact
from app.schemas.emergency_contact import EmergencyContactCreate
import uuid


class EmergencyContactCService:
    def __init__(
        self, 
        db: AsyncSession = Depends(get_db), 
        crud: EmergencyContactsCRUD = Depends(EmergencyContactsCRUD)
    ):
        self.db = db
        self.crud = crud
        
    async def create_emergency_contacts(self, contact_in: EmergencyContactCreate, user_id: uuid.UUID) -> EmergencyContact:
        create_data = contact_in.model_dump()
        create_data["user_id"] = user_id
        contact = await self.crud.create_emergency_contacts(create_data)
        await self.db.refresh(contact)
        return contact
    
    async def get_all_emergency_contact(self, user_id: uuid.UUID, skip: int = 0, limit: int = 1000) -> Sequence[EmergencyContact]:
        return await self.crud.emergency_contacts_for_user(user_id=user_id, skip=skip, limit=limit)