import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class JournalBase(BaseModel):  
    user_diary_entry: str | None = None
    author_diary_entry: str | None = None
    
class JournalCreate(JournalBase):
    user_id: uuid.UUID
    
class JournalUpdate(JournalBase):
    pass
    
class JournalRead(JournalBase):
    id: uuid.UUID
    user_id: uuid.UUID
    author_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)