import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from app.schemas.note import NoteCreate, NoteRead, NoteUpdate
from app.services.note import NoteService
from app.api.deps import get_current_user
from app.db.models.note import Note
from app.db.models.users import User


router = APIRouter()


@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_in: NoteCreate,
    note_service: NoteService = Depends(NoteService),
    current_user: User = Depends(get_current_user)
    ):
    return await note_service.create_note(note_in, current_user_id=current_user.id)


@router.get("", response_model=List[NoteRead])
async def read_note(
    skip: int = 0, 
    limit: int = 100,
    note_service: NoteService = Depends(NoteService),
    current_user: User = Depends(get_current_user)
):
    notes = await note_service.get_all_note(user_id=current_user.id, skip=skip, limit=limit)
    if not notes:
        return []
        
    return list(notes)


@router.patch("/{note_id}", response_model=NoteRead, status_code=status.HTTP_200_OK)
async def update_note(
    note_id: uuid.UUID,
    note_in: NoteUpdate,
    current_user: User = Depends(get_current_user),
    note_service: NoteService = Depends(NoteService)
):
    return await note_service.update_note(note_id, current_user.id, note_in)