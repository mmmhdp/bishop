import uuid

from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy.types import Text

from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from app.user.User import User


class ChatMessageBase (SQLModel):
    message: str | None = Field(default=None, sa_column=Column(Text))


class ChatMessageCreate (ChatMessageBase):
    pass


class ChatMessageUpdate (ChatMessageBase):
    message: str | None = Field(default=None, sa_column=Column(Text))


if TYPE_CHECKING:
    from app.user.User import User


class ChatMessage (ChatMessageBase, table=True):
    __tablename__ = "chat_message"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    message: str | None = Field(default=None, sa_column=Column(Text))
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: Optional["User"] = Relationship(back_populates="chat_messages")


class ChatMessagePublic (ChatMessageBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ChatMessagesPublic (SQLModel):
    data: list[ChatMessagePublic]
    count: int
