import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from app.schemas.reminder import ReminderCreate, ReminderRead, ReminderUpdate
from app.services.reminder import ReminderService
from app.api.deps import get_current_user
from app.db.models.reminder import Reminder
from app.db.models.users import User


router = APIRouter()


@router.post("", response_model=ReminderRead, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    reminder_in: ReminderCreate,
    reminder_service: ReminderService = Depends(ReminderService),
    current_user: User = Depends(get_current_user)
    ):
    return await reminder_service.create_reminder(reminder_in, user_id=current_user.id)


@router.get("", response_model=List[ReminderRead])
async def read_reminder(
    skip: int = 0, 
    limit: int = 100,
    reminder_service: ReminderService = Depends(ReminderService),
    current_user: User = Depends(get_current_user)
):
    reminders = await reminder_service.get_all_reminder(user_id=current_user.id, skip=skip, limit=limit)
    if not reminders:
        return []
        
    return list(reminders)


@router.patch("/{reminder_id}", response_model=ReminderRead, status_code=status.HTTP_200_OK)
async def update_reminder(
    reminder_id: uuid.UUID,
    reminder_in: ReminderUpdate,
    current_user: User = Depends(get_current_user),
    reminder_service: ReminderService = Depends(ReminderService)
):
    return await reminder_service.update_reminder(reminder_id, current_user.id, reminder_in)
