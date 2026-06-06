import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_model import BaseDBModel
from app.db.mixins import TimestampMixin
from datetime import datetime
import enum

if TYPE_CHECKING:
	from app.db.models.users import User


class MedicationType(str, enum.Enum):
	PILL = "Pill"
	LIQUID = "Liquid"
	INJECTION = "Injection"


class Medication(BaseDBModel, TimestampMixin):
	__tablename__: str = "medications"	
	id: Mapped[uuid.UUID] = mapped_column(
		primary_key=True,
		default=uuid.uuid4,
		index=True
	)
	user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	user: Mapped[Optional["User"]] = relationship(back_populates="medications")
	medication_type: Mapped[MedicationType] = mapped_column(String(255))
	medication_name: Mapped[str] = mapped_column(String(255))
	dosage: Mapped[str] = mapped_column(String(255))
	prescription_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)