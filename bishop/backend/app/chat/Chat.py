import uuid
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel, Column, Text, ForeignKey

from app.message.Message import Message


class ChatBase (SQLModel):
    avatar_id: uuid.UUID = Field(
        foreign_key="avatar.id", nullable=False, ondelete="CASCADE"
    )
    title: str | None = Field(sa_column=Column(
        Text, default="No title", nullable=False))


class ChatCreate (SQLModel):
    title: Optional[str] = Field(
        sa_column=Column(
            Text, default="No title", nullable=False
        )
    )


class ChatUpdate (SQLModel):
    title: str | None = Field(sa_column=Column(
        Text, default="No title", nullable=False))


if TYPE_CHECKING:
    from app.avatar.Avatar import Avatar


class Chat (ChatBase, table=True):
    __tablename__ = "chat"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    avatar_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey(
            "avatar.id", ondelete="CASCADE"), nullable=False)
    )
    title: Optional[str] = Field(default="No title")

    avatar: "Avatar" = Relationship(back_populates="chats")

    messages: list["Message"] = Relationship(
        back_populates="chat", cascade_delete=True)


class ChatPublic (SQLModel):
    id: uuid.UUID
    title: str | None = Field(default="No title")


class ChatsPublic (SQLModel):
    data: list[ChatPublic]
    count: int
