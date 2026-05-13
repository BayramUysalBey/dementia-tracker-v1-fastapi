import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_model import BaseDBModel
from app.db.mixins import TimestampMixin
from datetime import datetime
import enum
from pydantic import Field

if TYPE_CHECKING:
	from app.db.models.users import User


class ReminderType(str, enum.Enum):
	MEDICATION = "medication"
	HABIT = "habit"
	APPOINTMENT = "appointment"
	


class Reminder(BaseDBModel, TimestampMixin):
	__tablename__: str = "reminders"	
	id: Mapped[uuid.UUID] = mapped_column(
		primary_key=True,
		default=uuid.uuid4,
		index=True
	)	
	user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	related_entity_id: Mapped[uuid.UUID] = mapped_column(index=True, nullable=False)
	related_entity_type: Mapped[ReminderType] = mapped_column(String(255))
	date:Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
	name:Mapped[str] = mapped_column(String(255))
	type:Mapped[str] = mapped_column(String(255)) 
	repeat: Mapped[str] = mapped_column(String(255))
	check: Mapped[str] = mapped_column(String(255))