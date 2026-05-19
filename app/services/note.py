from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import  Depends
from app.db.session import get_db
from app.db.crud.note import NoteCRUD
from app.db.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate
import uuid
from fastapi import HTTPException, status, Depends


class NoteService:
    def __init__(
        self, 
        db: AsyncSession = Depends(get_db), 
        crud: NoteCRUD = Depends(NoteCRUD)
    ):
        self.db = db
        self.crud = crud
        
    async def create_note(self, create_in: NoteCreate, current_user_id: uuid.UUID) -> Note:
        create_data = create_in.model_dump()
        create_data["author_id"] = current_user_id
        note = await self.crud.create_note(create_data)
        await self.db.refresh(note)
        return note
        
    async def get_all_note(self, user_id: uuid.UUID, skip: int = 0, limit: int = 1000) -> Sequence[Note]:
        return await self.crud.note_for_user(user_id=user_id, skip=skip, limit=limit)
    
    async def update_note(self, note_id: uuid.UUID, user_id: uuid.UUID, user_in: NoteUpdate):
        db_object = await self.crud.get_note_by_id(note_id)
        if not db_object or db_object.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        update_data = user_in.model_dump(exclude_unset=True)
        updated_note = await self.crud.update_note(db_object, update_data)
        await self.db.refresh(updated_note)
        return updated_note