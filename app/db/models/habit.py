import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_model import BaseDBModel
from app.db.mixins import TimestampMixin
from sqlalchemy import Enum as SAEnum
from app.db.models.enums import RecordStatus


if TYPE_CHECKING:
	from app.db.models.users import User


class Habit(BaseDBModel, TimestampMixin):
	__tablename__: str = "habits"	
	id: Mapped[uuid.UUID] = mapped_column(
		primary_key=True,
		default=uuid.uuid4,
		index=True
	)	
	user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False) # Patient account deleted → their habits go with them. 
	                                                                                                       # The record was *about* them.
                                                                                                           # Caregiver account deleted → the habits **survive**, author becomes unknown.
	user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="habits")           # The patient's record shouldn't vanish because a caregiver left.
	author_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
	author: Mapped[Optional["User"]] = relationship("User", foreign_keys=[author_id], back_populates="habits_as_author")
	name: Mapped[str] = mapped_column(String(255))
	target_frequency: Mapped[str] = mapped_column(String(255))
	streak_count: Mapped[int] = mapped_column(Integer(), default=0)
	status: Mapped[RecordStatus] = mapped_column(
        SAEnum(
            RecordStatus,
            name="record_status",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ), # Without this, while SQLAlchemy stores the member *name* (`ACTIVE`), 
           # the database type holds the *value* (`active`), and every insertion operation fails.
        default=RecordStatus.ACTIVE,
        nullable=False,
    )