import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_model import BaseDBModel
from app.db.mixins import TimestampMixin
from enum import Enum


if TYPE_CHECKING:
	from app.db.models.users import User


class MonthlyReportType(str, Enum):
	USER_NOTE = "User Note"
	AUTHOR_NOTE = "Author Note"


class MonthlyReport(BaseDBModel, TimestampMixin):
	__tablename__: str = "monthly_reports"	
	id: Mapped[uuid.UUID] = mapped_column(
		primary_key=True,
		default=uuid.uuid4,
		index=True
	)
	user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="monthly_reports")
	author_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
	author: Mapped[Optional["User"]] = relationship("User", foreign_keys=[author_id], back_populates="monthly_reports_as_author")
	title: Mapped[str] = mapped_column(String(255))
	category: Mapped[str] = mapped_column(String(255))
	user_note: Mapped[str] = mapped_column(Text())
	author_note: Mapped[str] = mapped_column(Text())