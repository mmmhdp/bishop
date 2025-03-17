import uuid
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy.types import Text

from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from app.user.User import User

class SourceType(Enum):
    AUDIO = "audio"
    VIDEO = "video"

class TranscriptionBase (SQLModel):
    text: str = Field(default=None, sa_column=Column(Text))


class Transcription (TranscriptionBase, table=True):
    __tablename__ = "transcription"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    original_source: SourceType = Field(nullable=False)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: Optional["User"] | None = Relationship(back_populates="transcriptions")