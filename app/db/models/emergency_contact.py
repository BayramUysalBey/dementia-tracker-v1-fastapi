import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_model import BaseDBModel
from app.db.mixins import TimestampMixin


if TYPE_CHECKING:
	from app.db.models.users import User


class EmergencyContact(BaseDBModel, TimestampMixin):
	__tablename__: str = "emergency_contact"	
	id: Mapped[uuid.UUID] = mapped_column(
		primary_key=True,
		default=uuid.uuid4,
		index=True
	)
	first_name: Mapped[str] = mapped_column(String(255))
	last_name: Mapped[str] = mapped_column(String(255))
	user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
	user: Mapped[Optional["User"]] = relationship(back_populates="emergency_contacts")
	email: Mapped[str] = mapped_column(String(255), index=True)
	phone_number: Mapped[str] = mapped_column(String(255), index=True)
	relation: Mapped[str] = mapped_column(String(255))