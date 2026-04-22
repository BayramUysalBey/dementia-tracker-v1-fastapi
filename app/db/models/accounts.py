import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_model import BaseDBModel

if TYPE_CHECKING:
	from app.db.models.users import User



class Account(BaseDBModel):
	__tablename__: str = "accounts"
	id: Mapped[uuid.UUID] = mapped_column(
		primary_key=True,
		default=uuid.uuid4,
		index=True
	)
	type: Mapped[str] = mapped_column(String(255))
	billing_status: Mapped[str] = mapped_column(String(255), index=True)
	users: Mapped[List["User"]] = relationship(back_populates="account")