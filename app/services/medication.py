from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import  Depends
from app.db.session import get_db
from app.db.crud.medication import MedicationCRUD
from app.db.models.medication import Medication
from app.schemas.medication import MedicationCreate, MedicationUpdate
import uuid
from fastapi import HTTPException, status, Depends


class MedicationService:
    def __init__(
        self, 
        db: AsyncSession = Depends(get_db), 
        crud: MedicationCRUD = Depends(MedicationCRUD)
    ):
        self.db = db
        self.crud = crud
        
    async def create_medication(self, create_in: MedicationCreate, user_id: uuid.UUID) -> Medication:
        create_data = create_in.model_dump()
        create_data["user_id"] = user_id
        medication = await self.crud.create_medication(create_data)
        await self.db.refresh(medication)
        return medication
        
    async def get_all_medication(self, user_id: uuid.UUID, skip: int = 0, limit: int = 1000) -> Sequence[Medication]:
        return await self.crud.medication_for_user(user_id=user_id, skip=skip, limit=limit)
    
    async def update_medication(self, medication_id: uuid.UUID, user_id: uuid.UUID, user_in: MedicationUpdate) -> Medication:
        db_object = await self.crud.get_medication_by_id(medication_id)
        if not db_object or db_object.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")
        update_data = user_in.model_dump(exclude_unset=True)
        updated_medication = await self.crud.update_medication(db_object, update_data)
        await self.db.refresh(updated_medication)
        return updated_medication