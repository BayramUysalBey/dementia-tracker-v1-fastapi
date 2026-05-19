import uuid
from pydantic import BaseModel, ConfigDict
from app.db.models.habit import HabitType

class HabitBase(BaseModel):  
    name: str | None = None
    target_frequency: str | None = None
    streak_count: int | None = None
    
    
class HabitCreate(HabitBase):
    name: str | None = None
    target_frequency: str | None = None
    streak_count: int | None = None
    
    
class HabitUpdate(BaseModel):
    name: str | None = None
    target_frequency: str | None = None
    streak_count: int | None = None
    
    
class HabitRead(HabitBase):
    id: uuid.UUID
    user_id: uuid.UUID | None = None
    name: str | None = None
    target_frequency: str | None = None
    streak_count: int | None = None
    model_config = ConfigDict(from_attributes=True)