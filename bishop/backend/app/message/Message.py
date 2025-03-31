import uuid

from sqlmodel import Field, SQLModel, Column, Relationship, ForeignKey
from sqlalchemy.types import Text

from typing import TYPE_CHECKING, Optional


class MessageBase (SQLModel):
    text: Optional[str] = Field(default=None, sa_column=Column(Text))
    is_generated: bool = Field(default=False)
    dub_url: Optional[str] = Field(default=None, sa_column=Column(Text))


class MessageCreate(SQLModel):
    text: Optional[str] = Field(default=None, sa_column=Column(Text))
    is_generated: Optional[bool] = Field(default=False)
    dub_url: Optional[str] = Field(default=None, sa_column=Column(Text))


class MessageUpdate (SQLModel):
    text: str = Field(default=None, sa_column=Column(Text))


if TYPE_CHECKING:
    from app.chat.Chat import Chat


class Message(MessageBase, table=True):
    __tablename__ = "message"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    chat: "Chat" = Relationship(back_populates="messages")
    chat_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey(
            "chat.id", ondelete="CASCADE"), nullable=False)
    )
    avatar_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey(
            "avatar.id", ondelete="CASCADE"), nullable=False)
    )
    user_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey(
            "user.id", ondelete="CASCADE"), nullable=False)
    )


class MessagePublic (MessageBase):
    id: uuid.UUID
    chat_id: uuid.UUID
    avatar_id: uuid.UUID


class MessagesPublic (SQLModel):
    data: list[MessagePublic]
    count: int
