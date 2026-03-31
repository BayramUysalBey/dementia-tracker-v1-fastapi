import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base


from app.db.base_model import BaseDBModel
from app.db.mixins import TimestampMixin


class User(BaseDBModel, TimestampMixin):
	__tablename__: str = "users"	
	id: Mapped[uuid.UUID] = mapped_column(
		primary_key=True,
		default=uuid.uuid4,
		index=True
	)
	name: Mapped[str] = mapped_column(String(255))
	email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
	hashed_password: Mapped[str] = mapped_column(String(255))
	username: Mapped[str] = mapped_column(String(255), unique=True, index=True)
	last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
	invited_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)

	inviter: Mapped[Optional["User"]] = relationship(
		"User",
		remote_side=[id],
		back_populates="invitees"
	)
	invitees: Mapped[List["User"]] = relationship(
		"User",
		back_populates="inviter"
	)