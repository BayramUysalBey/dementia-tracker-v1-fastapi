import uuid
from typing import List
from fastapi import APIRouter, Depends, status, File, UploadFile, Form
from app.schemas.media import MediaRead, MediaUpdate
from app.services.media import MediaService
from app.api.deps import get_current_user
from app.db.models.media import MediaType
from app.db.models.users import User


router = APIRouter()


@router.post("", response_model=MediaRead, status_code=status.HTTP_201_CREATED)
async def create_media(
    file: UploadFile = File(...), 
    name: str = Form(...),
    type: MediaType = Form(...),
    journal_id: uuid.UUID | None = Form(None),   
    media_service: MediaService = Depends(MediaService),
    current_user: User = Depends(get_current_user)
):
    return await media_service.create_media(
        file=file, 
        name=name, 
        type=type, 
        journal_id=journal_id, 
        user_id=current_user.id
    )


@router.get("", response_model=List[MediaRead])
async def read_media(
    skip: int = 0, 
    limit: int = 100,
    media_service: MediaService = Depends(MediaService),
    current_user: User = Depends(get_current_user)
):
    medias = await media_service.get_all_media(user_id=current_user.id, skip=skip, limit=limit)
    if not medias:
        return []
        
    return list(medias)


@router.patch("/{media_id}", response_model=MediaRead, status_code=status.HTTP_200_OK)
async def update_media(
    media_id: uuid.UUID,
    media_in: MediaUpdate,
    current_user: User = Depends(get_current_user),
    media_service: MediaService = Depends(MediaService)
):
    return await media_service.update_media(media_id, current_user.id, media_in)
