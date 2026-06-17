from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import  Depends
from app.db.session import get_db
from app.db.crud.emergency_contact import EmergencyContactsCRUD
from app.db.models.emergency_contact import EmergencyContact
from app.schemas.emergency_contact import EmergencyContactCreate, EmergencyContactUpdate
import uuid
from fastapi import HTTPException, status


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
        return await self.crud.emergency_contacts_for_user(user_id=user_id)

    async def update_emergency_contact(
        self, contact_id: uuid.UUID, user_id: uuid.UUID, contact_in: EmergencyContactUpdate
    ) -> EmergencyContact:
        db_object = await self.crud.get_emergency_contact_by_id(contact_id)
        if not db_object or db_object.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergency contact not found")
        update_data = contact_in.model_dump(exclude_unset=True)
        updated_contact = await self.crud.update_emergency_contacts(db_object, update_data)
        await self.db.refresh(updated_contact)
        return updated_contact
