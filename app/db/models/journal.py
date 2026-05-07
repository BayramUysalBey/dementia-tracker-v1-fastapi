import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_model import BaseDBModel
from app.db.mixins import TimestampMixin

if TYPE_CHECKING:
	from app.db.models.users import User


class Journal(BaseDBModel, TimestampMixin):
	__tablename__: str = "journals"	
	id: Mapped[uuid.UUID] = mapped_column(
		primary_key=True,
		default=uuid.uuid4,
		index=True
	)
	user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="journals_as_patient")
	author_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
	author: Mapped[Optional["User"]] = relationship("User", foreign_keys=[author_id], back_populates="journals_as_author")	
	user_diary_entry: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
	author_diary_entry: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)