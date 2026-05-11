import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class JournalBase(BaseModel):  
    user_diary_entry: str | None = None
    author_diary_entry: str | None = None
    
class JournalCreate(JournalBase):
    user_id: uuid.UUID
    
class JournalUpdate(JournalBase):
    pass
    
class JournalRead(JournalBase):
    id: uuid.UUID
    user_id: uuid.UUID
    author_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
    




	# class Journal(BaseDBModel, TimestampMixin):
	# __tablename__: str = "journals"	
	# id: Mapped[uuid.UUID] = mapped_column(
	# 	primary_key=True,
	# 	default=uuid.uuid4,
	# 	index=True
	# )
	# user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	# user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[user_id], back_populates="journals_as_patient")
	# author_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
	# author: Mapped[Optional["User"]] = relationship("User", foreign_keys=[author_id], back_populates="journals_as_author")	
	# user_diary_entry: Mapped[str] = mapped_column(String(255))
	# author_diary_entry: Mapped[str] = mapped_column(String(255))