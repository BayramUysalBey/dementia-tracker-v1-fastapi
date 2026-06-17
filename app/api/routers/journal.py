import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from app.schemas.journal import JournalCreate, JournalRead, JournalUpdate
from app.services.journal import JournalService
from app.api.deps import get_current_user
from app.db.models.users import User


router = APIRouter()


@router.post("", response_model=JournalRead, status_code=status.HTTP_201_CREATED)
async def create_journal(
    journal_in: JournalCreate,
    journal_service: JournalService = Depends(JournalService),
    current_user: User = Depends(get_current_user)
    ):
    return await journal_service.create_journal(journal_in, current_user_id=current_user.id)


@router.get("", response_model=List[JournalRead])
async def read_journal(
    skip: int = 0, 
    limit: int = 100,
    journal_service: JournalService = Depends(JournalService),
    current_user: User = Depends(get_current_user)
):
    journals = await journal_service.get_all_journal(user_id=current_user.id, skip=skip, limit=limit)
    if not journals:
        return []
        
    return list(journals)


@router.patch("/{journal_id}", response_model=JournalRead, status_code=status.HTTP_200_OK)
async def update_journal(
    journal_id: uuid.UUID,
    journal_in: JournalUpdate,
    current_user: User = Depends(get_current_user),
    journal_service: JournalService = Depends(JournalService)
):
    return await journal_service.update_journal(journal_id, current_user.id, journal_in)
