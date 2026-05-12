import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.db.models.reminder import ReminderType

class ReminderBase(BaseModel):  
    related_entity_id: uuid.UUID
    related_entity_type: ReminderType | None = None
    name: str | None = None
    repeat: str | None = None
    
class ReminderCreate(ReminderBase):
    type: str
    check: str
    
class ReminderUpdate(BaseModel):
    related_entity_type: ReminderType | None = None
    name: str | None = None
    date: datetime | None = None
    repeat: str | None = None
    
class ReminderRead(ReminderBase):
    id: uuid.UUID
    user_id: uuid.UUID | None = None
    related_entity_id: uuid.UUID
    name: str | None = None
    type: str | None = None
    date: datetime | None = None
    check: str | None = None
    model_config = ConfigDict(from_attributes=True)