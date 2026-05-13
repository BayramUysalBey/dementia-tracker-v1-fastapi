import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from app.schemas.medication import MedicationCreate, MedicationRead, MedicationUpdate
from app.services.medication import MedicationService
from app.api.deps import get_current_user
from app.db.models.medication import Medication
from app.db.models.users import User


router = APIRouter()


@router.post("", response_model=MedicationRead, status_code=status.HTTP_201_CREATED)
async def create_medication(
    medication_in: MedicationCreate,
    medication_service: MedicationService = Depends(MedicationService),
    current_user: User = Depends(get_current_user)
    ):
    return await medication_service.create_medication(medication_in, user_id=current_user.id)


@router.get("", response_model=List[MedicationRead])
async def read_medication(
    skip: int = 0, 
    limit: int = 100,
    medication_service: MedicationService = Depends(MedicationService),
    current_user: User = Depends(get_current_user)
):
    medications = await medication_service.get_all_medication(user_id=current_user.id, skip=skip, limit=limit)
    if not medications:
        return []
        
    return list(medications)


@router.patch("/{medication_id}", response_model=MedicationRead, status_code=status.HTTP_200_OK)
async def update_medication(
    medication_id: uuid.UUID,
    medication_in: MedicationUpdate,
    current_user: User = Depends(get_current_user),
    medication_service: MedicationService = Depends(MedicationService)
):
    return await medication_service.update_medication(medication_id, current_user.id, medication_in)