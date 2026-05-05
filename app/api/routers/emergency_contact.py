import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from app.schemas.emergency_contact import EmergencyContactCreate, EmergencyContactRead
from app.services.emergency_contact import EmergencyContactCService
from app.api.deps import get_current_user
from app.db.models.users import User


router = APIRouter()


@router.post("", response_model=EmergencyContactRead, status_code=status.HTTP_201_CREATED)
async def create_emergency_contact(
    contact_in: EmergencyContactCreate,
    contact_service: EmergencyContactCService = Depends(EmergencyContactCService),
    current_user: User = Depends(get_current_user)
    ):
    return await contact_service.create_emergency_contacts(contact_in, user_id=current_user.id)


@router.get("", response_model=List[EmergencyContactRead])
async def read_emergency_contacts(
    skip: int = 0, 
    limit: int = 100,
    emergency_contact_service: EmergencyContactCService = Depends(EmergencyContactCService),
    current_user: User = Depends(get_current_user)
):
    emergency_contacts = await emergency_contact_service.get_all_emergency_contact(user_id=current_user.id, skip=skip, limit=limit)
    if not emergency_contacts:
        return []
        
    return list(emergency_contacts)