import uuid
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from app.db.models.medication import MedicationType

class MedicationBase(BaseModel):  
    medication_type: MedicationType | None = None
    medication_name: str | None = None
    dosage: str | None = Field(None, pattern=r"^\d+\s?(mg|ml|g)$") 
    
class MedicationCreate(MedicationBase):
    pass
    
class MedicationUpdate(BaseModel):
    medication_type: MedicationType | None = None
    medication_name: str | None = None
    dosage: str | None = None
    prescription_date: datetime | None = None
    
class MedicationRead(MedicationBase):
    id: uuid.UUID
    user_id: uuid.UUID | None = None
    medication_type: MedicationType | None = None
    medication_name: str | None = None
    dosage: str | None = None
    prescription_date: datetime | None = None
    model_config = ConfigDict(from_attributes=True)
    