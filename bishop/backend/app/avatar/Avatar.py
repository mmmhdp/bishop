import uuid

from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy.types import Text
from typing import TYPE_CHECKING, Optional

from app.chat.Chat import Chat

if TYPE_CHECKING:
    from app.user.User import User


class AvatarBase (SQLModel):
    name: str = Field(sa_column=Column(Text, nullable=False))


class AvatarCreate (AvatarBase):
    name: str = Field(sa_column=Column(Text, nullable=False))


class AvatarUpdate (AvatarBase):
    name: str = Field(sa_column=Column(Text, nullable=False))


class Avatar (AvatarBase, table=True):
    __tablename__ = "avatar"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    weight_url: str | None = Field(default=None, sa_column=(Text))
    user: Optional["User"] = Relationship(back_populates="avatars")
    chats: list["Chat"] = Relationship(
        back_populates="avatar", cascade_delete=True)


class AvatarPublic(AvatarBase):
    "Avatar Public Interface"
    id: uuid.UUID
    name: str


class AvatarsPublic(SQLModel):
    data: list[AvatarPublic]
    count: int
