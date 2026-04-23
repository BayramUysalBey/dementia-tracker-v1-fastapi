from pydantic import BaseModel
import uuid
from typing import Literal

class AccountBase(BaseModel):
	type: Literal["pro", "personal"]
	billing_status: Literal["active", "inactive", "suspended"] = "active"

class AccountCreate(AccountBase):
	pass

class AccountRead(BaseModel):
	id: uuid.UUID
	type: str
	billing_status: str