import uuid
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from app.db.models.medication import MedicationType
from app.db.models.enums import RecordStatus

class MedicationBase(BaseModel):  
    medication_type: MedicationType
    medication_name: str
    dosage: str
    
class MedicationCreate(MedicationBase):
    model_config = ConfigDict(extra="forbid")
    user_id: uuid.UUID
    dosage: str = Field(pattern=r"^\d+\s?(mg|ml|g)$")
    prescription_date: datetime | None = None
    
class MedicationUpdate(BaseModel):
    # Unknown fields are rejected: a PATCH that silently ignored one would
    # return 200 for a change it never made.
    # user_id is deliberately absent: changing it would move the medication to
    # another patient without the care-assignment check that create enforces.
    model_config = ConfigDict(extra="forbid")
    medication_type: MedicationType | None = None
    medication_name: str | None = None
    dosage: str | None = Field(None, pattern=r"^\d+\s?(mg|ml|g)$")
    prescription_date: datetime | None = None
    status: RecordStatus | None = None
    
class MedicationRead(MedicationBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    author_id: uuid.UUID | None
    prescription_date: datetime | None = None
    status: RecordStatus