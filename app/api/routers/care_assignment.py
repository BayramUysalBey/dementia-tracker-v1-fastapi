import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from app.schemas.care_assignment import CareAssignmentCreate, CareAssignmentRead
from app.services.care_assignment import CareAssignmentService
from app.api.deps import get_current_user
from app.db.models.users import User


router = APIRouter()


@router.post("", response_model=CareAssignmentRead, status_code=status.HTTP_201_CREATED)
async def assign_patient(
    assignment_in: CareAssignmentCreate,
    current_user: User = Depends(get_current_user),
    service: CareAssignmentService = Depends(CareAssignmentService)
):
    return await service.assign_patient(
        caregiver_id=current_user.id,
        patient_id=assignment_in.patient_id
    )


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unassign_patient(
    patient_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: CareAssignmentService = Depends(CareAssignmentService)
):
    await service.unassign_patient(
        caregiver_id=current_user.id,
        patient_id=patient_id
    )


@router.get("", response_model=List[CareAssignmentRead])
async def list_my_patients(
    current_user: User = Depends(get_current_user),
    service: CareAssignmentService = Depends(CareAssignmentService)
):
    return await service.list_my_patients(caregiver_id=current_user.id)