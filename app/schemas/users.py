import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

class UserBase(BaseModel):
    first_name: str
    last_name: str
    role: str
    email: EmailStr
    username: str | None = None
    
class UserCreate(UserBase):
    password: str
    username: str | None = None
    
class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    password: str | None = None
    
class UserRead(UserBase):
    id: uuid.UUID
    account_id: uuid.UUID | None = None
    last_login: datetime | None = None
    invited_by: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)