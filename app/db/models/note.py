import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, BOOLEAN, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_model import BaseDBModel
from app.db.mixins import TimestampMixin
from enum import Enum


if TYPE_CHECKING:
	from app.db.models.users import User


class NoteType(str, Enum):
	SYNDROME = "Syndrome"
	MEDICATION_MONITORING = "Medication Monitoring"
	MOOD = "Mood"


class Note(BaseDBModel, TimestampMixin):
	__tablename__: str = "notes"	
	id: Mapped[uuid.UUID] = mapped_column(
		primary_key=True,
		default=uuid.uuid4,
		index=True
	)
	user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="notes")
	author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
	author: Mapped[Optional["User"]] = relationship("User", foreign_keys=[author_id], back_populates="notes_as_author")
	title: Mapped[str] = mapped_column(String(255))
	content: Mapped[str] = mapped_column(Text())
	category: Mapped[str] = mapped_column(String(255))
	type: Mapped[str] = mapped_column(String(255))
	is_checklist: Mapped[bool] = mapped_column(BOOLEAN)