import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import Depends
from app.db.session import get_db
from app.db.models.care_assignment import CareAssignment


class CareAssignmentCRUD:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def create(self, caregiver_id: uuid.UUID, patient_id: uuid.UUID) -> CareAssignment:
        assignment = CareAssignment(caregiver_id=caregiver_id, patient_id=patient_id)
        self.db.add(assignment)
        await self.db.flush()
        return assignment

    async def get(self, caregiver_id: uuid.UUID, patient_id: uuid.UUID) -> CareAssignment | None:
        result = await self.db.execute(
            select(CareAssignment).where(
                CareAssignment.caregiver_id == caregiver_id,
                CareAssignment.patient_id == patient_id
            )
        )
        return result.scalar_one_or_none()

    async def list_patients(self, caregiver_id: uuid.UUID) -> Sequence[CareAssignment]:
        result = await self.db.execute(
            select(CareAssignment).where(CareAssignment.caregiver_id == caregiver_id)
        )
        return result.scalars().all()

    async def delete(self, caregiver_id: uuid.UUID, patient_id: uuid.UUID) -> bool:
        result = await self.db.execute(
            delete(CareAssignment)
            .where(
                CareAssignment.caregiver_id == caregiver_id,
                CareAssignment.patient_id == patient_id
            )
            .returning(CareAssignment.id) # tells PostgreSQL to send back the id of whatever row it deleted
        )
        await self.db.flush()
        return result.scalar_one_or_none() is not None