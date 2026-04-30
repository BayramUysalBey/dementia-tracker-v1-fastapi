import uuid
from pydantic import BaseModel, EmailStr, ConfigDict


class EmergencyContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    relation: str
    
class EmergencyContactCreate(EmergencyContactBase):
    pass
    
class EmergencyContactUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None
    relation: str | None = None
    
class UEmergencyContactRead(EmergencyContactBase):
    id: uuid.UUID
    user_id: uuid.UUID | None = None
    model_config = ConfigDict(from_attributes=True)