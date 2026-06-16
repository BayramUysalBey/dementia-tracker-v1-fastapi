from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import  Depends, UploadFile
from app.db.session import get_db
from app.db.crud.media import MediaCRUD
from app.db.models.media import MediaType, Media
from app.schemas.media import MediaUpdate
import uuid
from fastapi import HTTPException, status, Depends
import os
from pathlib import Path
from app.core.settings import settings
import asyncio


class MediaService:
    def __init__(
        self, 
        db: AsyncSession = Depends(get_db), 
        crud: MediaCRUD = Depends(MediaCRUD)
    ):
        self.db = db
        self.crud = crud
        
    async def create_media(
        self, 
        file: UploadFile,
        name: str,
        type: MediaType, 
        journal_id: uuid.UUID | None,
		user_id: uuid.UUID) -> Media:
        os.makedirs(settings.MEDIA_UPLOAD_DIR, exist_ok=True)
        
        ALLOWED_EXTENSIONS = {
            MediaType.PHOTO: [".jpg", ".jpeg", ".png", ".webp"],
            MediaType.VOICE_MEMO: [".mp3", ".wav", ".m4a", ".ogg"],
            MediaType.VIDEO: [".mp4", ".mkv", ".mov", ".webm"]
        }
        file_extension = Path(file.filename or "").suffix.lower()
        if file_extension not in ALLOWED_EXTENSIONS[type]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file extension '{file_extension}' for media type '{type.value}'"
            )
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(settings.MEDIA_UPLOAD_DIR, unique_filename)
        MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

        def write_file():
            total = 0
            with open(file_path, "wb") as buffer:
                while chunk := file.file.read(1024 * 1024):  # read 1 MB at a time
                    total += len(chunk)
                    if total > MAX_FILE_SIZE:
                        buffer.close()
                        os.remove(file_path)
                        raise ValueError("File too large")
                    buffer.write(chunk)

        try:
            await asyncio.to_thread(write_file)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=str(e)
            )

        real_media_url = f"/{settings.MEDIA_UPLOAD_DIR}/{unique_filename}"
        create_data = {
            "user_id": user_id,
            "journal_id": journal_id,
            "name": name,
            "type": type,
            "media_url": real_media_url
        }
        try:
            media = await self.crud.create_media(create_data)
            await self.db.refresh(media)
            return media
        except Exception:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise
        
    async def get_all_media(self, user_id: uuid.UUID, skip: int = 0, limit: int = 1000) -> Sequence[Media]:
        return await self.crud.media_for_user(user_id=user_id, skip=skip, limit=limit)
    

    async def update_media(self, media_id: uuid.UUID, user_id: uuid.UUID, user_in: MediaUpdate) -> Media:
        db_object = await self.crud.get_media_by_id(media_id)
        if not db_object or db_object.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")
        update_data = user_in.model_dump(exclude_unset=True)
        updated_media = await self.crud.update_media(db_object, update_data)
        await self.db.refresh(updated_media)
        return updated_media