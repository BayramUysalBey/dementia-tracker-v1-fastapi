import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_model import BaseDBModel
from app.db.mixins import TimestampMixin
import enum



class MediaType(str, enum.Enum):
	PHOTO = "photo"
	VOICE_MEMO = "voice memo"
	VIDEO = "video"


class Media(BaseDBModel, TimestampMixin):
	__tablename__: str = "medias"	
	id: Mapped[uuid.UUID] = mapped_column(
		primary_key=True,
		default=uuid.uuid4,
		index=True
	)	
	user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	journal_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("journals.id", ondelete="SET NULL"), nullable=True)
	media_url: Mapped[str] = mapped_column(String(255))
	name: Mapped[str] = mapped_column(String(255))
	type: Mapped[MediaType] = mapped_column(String(255))