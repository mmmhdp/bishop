import uuid

from sqlmodel import Field, SQLModel, Column, Relationship
from sqlalchemy.types import Text

from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from app.chat.Chat import Chat


class MessageBase (SQLModel):
    id: uuid.UUID
    text: Optional[str] = Field(default=None, sa_column=Column(Text))
    is_generated: bool = Field(default=False)
    dub_url: Optional[str] = Field(default=None, sa_column=Column(Text))


class MessageCreate(SQLModel):
    text: Optional[str] = Field(default=None, sa_column=Column(Text))
    is_generated: Optional[bool] = Field(default=False)
    dub_url: Optional[str] = Field(default=None, sa_column=Column(Text))


class MessageUpdate (SQLModel):
    text: str = Field(default=None, sa_column=Column(Text))


class Message(MessageCreate, table=True):
    __tablename__ = "message"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    chat: Optional["Chat"] = Relationship(back_populates="messages")
    chat_id: uuid.UUID = Field(foreign_key="chat.id", nullable=False)
    avatar_id: uuid.UUID = Field(foreign_key="avatar.id", nullable=False)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)


class MessagePublic (MessageBase):
    pass


class MessagesPublic (SQLModel):
    data: list[MessagePublic]
    count: int
