import uuid
from pydantic import BaseModel, ConfigDict
from app.db.models.enums import RecordStatus


class HabitBase(BaseModel):
    """Fields every habit has. Both are NOT NULL in the database."""
    name: str
    target_frequency: str


class HabitCreate(HabitBase):
    model_config = ConfigDict(extra="forbid")


class HabitUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")   # extra="forbid"` means a client sending a field you later 
                                                # removed gets a hard failure rather than being quietly tolerated.
    name: str | None = None
    target_frequency: str | None = None
    status: RecordStatus | None = None


class HabitRead(HabitBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    streak_count: int
    status: RecordStatus