import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_model import BaseDBModel
from app.db.mixins import TimestampMixin
from enum import Enum

if TYPE_CHECKING:
	from app.db.models.users import User



class HabitType(str, Enum ):
	EXERCISE = "exercise"
	READING_BOOK = "reading book"


class Habit(BaseDBModel, TimestampMixin):
	__tablename__: str = "habits"	
	id: Mapped[uuid.UUID] = mapped_column(
		primary_key=True,
		default=uuid.uuid4,
		index=True
	)	
	user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	user: Mapped["User"] = relationship("User", back_populates="habits")
	name: Mapped[str] = mapped_column(String(255))
	target_frequency: Mapped[str] = mapped_column(String(255))
	streak_count: Mapped[int] = mapped_column(Integer())