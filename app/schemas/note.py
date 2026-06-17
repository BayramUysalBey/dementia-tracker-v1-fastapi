import uuid
from pydantic import BaseModel, ConfigDict
from app.db.models.note import NoteType

class NoteBase(BaseModel):
    title: str | None = None
    content: str | None = None
    category: NoteType | None = None
    type: NoteType | None = None
    is_checklist: bool | None = None

       
class NoteCreate(NoteBase):
   user_id: uuid.UUID
   title: str | None = None
   content: str | None = None
   category: NoteType | None = None
   type: NoteType | None = None
   is_checklist: bool | None = None
    

class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    category: NoteType | None = None
    type: NoteType | None = None
    is_checklist: bool | None = None
    
    
class NoteRead(NoteBase):
    id: uuid.UUID
    user_id: uuid.UUID
    author_id: uuid.UUID
    title: str | None = None
    content: str | None = None
    category: NoteType | None = None
    type: NoteType | None = None
    is_checklist: bool | None = None
    model_config = ConfigDict(from_attributes=True)