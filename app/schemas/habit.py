import uuid
from pydantic import BaseModel, ConfigDict
from app.db.models.enums import RecordStatus


class HabitBase(BaseModel):
    """Fields every habit has. Both are NOT NULL in the database."""
    name: str
    target_frequency: str


class HabitCreate(HabitBase):
    user_id: uuid.UUID
    model_config = ConfigDict(extra="forbid")


class HabitUpdate(BaseModel):
    # Unknown fields are rejected: a PATCH that silently ignored one would
    # return 200 for a change it never made.
    # user_id is deliberately absent: changing it would move the habit to
    # another patient without the care-assignment check that create enforces.   
    model_config = ConfigDict(extra="forbid")   
    name: str | None = None
    target_frequency: str | None = None
    status: RecordStatus | None = None


class HabitRead(HabitBase):
    model_config = ConfigDict(from_attributes=True)
    author_id: uuid.UUID | None
    id: uuid.UUID
    user_id: uuid.UUID
    streak_count: int
    status: RecordStatus