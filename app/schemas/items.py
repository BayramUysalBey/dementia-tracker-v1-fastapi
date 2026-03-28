from pydantic import BaseModel
from typing import List, Optional

class Item(BaseModel):
    id: int
    name: str
    price: float
    is_offer: bool = False
    user_id: int
    category: str

class ItemCreate(BaseModel):
    name: str
    price: float
    is_offer: Optional[bool] = False
    user_id: int
    category: str

class FileUploadResponse(BaseModel):
    filename: str | None
    content_type: str | None
