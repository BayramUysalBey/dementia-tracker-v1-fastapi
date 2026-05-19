import uuid
from pydantic import BaseModel, ConfigDict
from app.db.models.media import MediaType

class MediaBase(BaseModel):  
    user_id: uuid.UUID
    type: MediaType | None = None
    media_url: str | None = None
    name: str | None = None
    
class MediaCreate(MediaBase):
    file: str | None = None
    name: str | None = None
    type: MediaType | None = None
    
    
class MediaUpdate(BaseModel):
    name: str | None = None
    media_url: str | None = None
    type: str | None = None
    
class MediaRead(MediaBase):
    id: uuid.UUID
    user_id: uuid.UUID | None = None
    name: str | None = None
    type: str | None = None
    model_config = ConfigDict(from_attributes=True)