import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CareAssignmentCreate(BaseModel):
    patient_id: uuid.UUID


class CareAssignmentRead(BaseModel):
    id: uuid.UUID
    caregiver_id: uuid.UUID
    patient_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)