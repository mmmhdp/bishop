import uuid

from sqlmodel import Field, SQLModel, Column
from sqlalchemy.types import Text

from typing import TYPE_CHECKING, Optional


#if TYPE_CHECKING:
    # TODO: from app.chat.Chat import Chat


class MessageBase (SQLModel):
    text: str | None = Field(default=None, sa_column=Column(Text))


class MessageCreate (MessageBase):
    chat_id: uuid.UUID = Field(
        foreign_key="chat.id", nullable=False, ondelete="CASCADE"
    )


class MessageUpdate (MessageBase):
    text: str | None = Field(default=None, sa_column=Column(Text))


class Message (MessageCreate, table=True):
    __tablename__ = "message"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    is_avatar: bool = Field(default=False, nullable=False)

class MessagePublic (MessageBase):
    id: uuid.UUID

class MessagesPublic (SQLModel):
    data: list[MessagePublic]
    count: int
