import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.medication import Medication
from app.db.session import get_db
from fastapi import Depends


class MedicationCRUD:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
    
    async def create_medication(self, obj_in: dict) -> Medication:
        db_object = Medication(**obj_in)
        self.db.add(db_object)
        await self.db.flush()
        return db_object

    async def medication_for_user(self, user_id: uuid.UUID) -> Sequence[Medication]:
        result = await self.db.execute(select(Medication).where(Medication.user_id == user_id))
        return result.scalars().all()

    async def update_medication(self, db_object: Medication, obj_in: dict) -> Medication:
        for field, value in obj_in.items():
            if hasattr(db_object, field):
                setattr(db_object, field, value)
                await self.db.flush()
        return db_object
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[Medication]:
        result = await self.db.execute(select(Medication).offset(skip).limit(limit))
        return result.scalars().all()
    
    async def get_medication_by_id(self, medication_id: uuid.UUID) -> Medication | None:
        result = await self.db.execute(select(Medication).where(Medication.id == medication_id))
        return result.scalars().first()
