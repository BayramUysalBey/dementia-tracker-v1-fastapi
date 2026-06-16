import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from app.db.session import get_db
from app.db.crud.care_assignment import CareAssignmentCRUD
from app.db.crud.users import UserCRUD
from app.db.models.care_assignment import CareAssignment
from app.db.models.users import UserRole
from typing import Sequence


class CareAssignmentService:
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
        crud: CareAssignmentCRUD = Depends(CareAssignmentCRUD)
    ):
        self.db = db
        self.crud = crud

    async def assign_patient(
        self, caregiver_id: uuid.UUID, patient_id: uuid.UUID
    ) -> CareAssignment:
        user_crud = UserCRUD(self.db)

        caregiver = await user_crud.get_by_id(caregiver_id)
        if not caregiver or caregiver.role != UserRole.CAREGIVER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only caregivers can be assigned patients"
            )

        patient = await user_crud.get_by_id(patient_id)
        if not patient or patient.role != UserRole.PATIENT:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )

        existing = await self.crud.get(caregiver_id, patient_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This patient is already assigned to you"
            )

        assignment = await self.crud.create(caregiver_id, patient_id)
        await self.db.refresh(assignment)
        return assignment

    async def unassign_patient(
        self, caregiver_id: uuid.UUID, patient_id: uuid.UUID
    ) -> None:
        deleted = await self.crud.delete(caregiver_id, patient_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )

    async def list_my_patients(
        self, caregiver_id: uuid.UUID
    ) -> Sequence[CareAssignment]:
        return await self.crud.list_patients(caregiver_id)

    async def verify_caregiver_access(
        self, caregiver_id: uuid.UUID, patient_id: uuid.UUID
    ) -> None:
        assignment = await self.crud.get(caregiver_id, patient_id)
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to this patient"
            )