import uuid
from pydantic import BaseModel, ConfigDict
from app.db.models.enums import RecordStatus

class HabitBase(BaseModel):  
    name: str | None = None
    target_frequency: str | None = None
    streak_count: int | None = None
    
    
class HabitCreate(HabitBase):
    pass
    
    
class HabitUpdate(BaseModel):
    name: str | None = None
    target_frequency: str | None = None
    streak_count: int | None = None
    status: RecordStatus | None = None
    
    
class HabitRead(HabitBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID | None = None
    name: str | None = None
    target_frequency: str | None = None
    streak_count: int | None = None
    status: RecordStatus