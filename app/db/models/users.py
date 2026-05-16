import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_model import BaseDBModel
from app.db.mixins import TimestampMixin
from enum import Enum

if TYPE_CHECKING:
	from app.db.models.emergency_contact import EmergencyContact
	from app.db.models.accounts import Account
	from app.db.models.medication import Medication
	from app.db.models.journal import Journal

class UserRole(str, Enum):
	__tablename__: str = "usersrole"
	CAREGIVER = "caregiver"
	PATIENT = "patient"
	FAMILY = "family"
	DOCTOR = "doctor"

class User(BaseDBModel, TimestampMixin):
	__tablename__: str = "users"	
	id: Mapped[uuid.UUID] = mapped_column(
		primary_key=True,
		default=uuid.uuid4,
		index=True
	)
	first_name: Mapped[str] = mapped_column(String(255))
	last_name: Mapped[str] = mapped_column(String(255))
	role: Mapped[UserRole] = mapped_column(String(255))
	account: Mapped[Optional["Account"]] = relationship(back_populates="users")
	account_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
	email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
	hashed_password: Mapped[str] = mapped_column(String(255))
	username: Mapped[str] = mapped_column(String(255), unique=True, index=True)
	last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
	invited_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
	inviter: Mapped[Optional["User"]] = relationship(
		"User",
		remote_side=[id],
		back_populates="invitees"
	)
	invitees: Mapped[List["User"]] = relationship(
		"User",
		back_populates="inviter"
	)
	emergency_contacts: Mapped[List["EmergencyContact"]] = relationship(
       "EmergencyContact", 
       back_populates="user",
	   cascade="all, delete-orphan")
	medications: Mapped[List["Medication"]] = relationship(
		"Medication",
		back_populates="user",
		cascade="all, delete-orphan"
	)
	journals_as_patient: Mapped[List["Journal"]] = relationship(
		"Journal",
		foreign_keys="[Journal.user_id]",
		back_populates="user",
		cascade="all, delete-orphan"
	)
	journals_as_author: Mapped[List["Journal"]] = relationship(
		"Journal",
		foreign_keys="[Journal.author_id]",
		back_populates="author",
		cascade="all, delete-orphan"
	)
