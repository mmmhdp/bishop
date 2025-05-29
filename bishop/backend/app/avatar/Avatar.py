import uuid

from sqlmodel import Field, Relationship, SQLModel, Column, ForeignKey
from sqlalchemy.types import Text
from typing import TYPE_CHECKING, Optional

from app.chat.Chat import Chat
from app.train_material.TrainMaterial import TrainMaterial


class AvatarBase (SQLModel):
    name: str = Field(sa_column=Column(Text, nullable=False))
    weight_url: Optional[str] = Field(default=None)
    voice_url: Optional[str] = Field(default=None)
    status: str = Field(sa_column=Column(Text, nullable=False))


class AvatarCreate (SQLModel):
    name: str = Field(sa_column=Column(Text, nullable=False))


class AvatarUpdate (SQLModel):
    name: str = Field(sa_column=Column(Text, nullable=False))


class AvatarUpdateStatus (SQLModel):
    status: str = Field(sa_column=Column(Text, nullable=False))


if TYPE_CHECKING:
    from app.user.User import User


class Avatar (AvatarBase, table=True):
    __tablename__ = "avatar"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    user_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey(
            "user.id", ondelete="CASCADE"), nullable=False)
    )
    status: str = Field(sa_column=Column(Text, nullable=False))
    voice_url: Optional[str] = Field(default=None, sa_column=(Text))
    weight_url: Optional[str] = Field(default=None, sa_column=(Text))
    user: Optional["User"] = Relationship(back_populates="avatars")
    chats: list["Chat"] = Relationship(
        back_populates="avatar", cascade_delete=True)
    train_materials: list["TrainMaterial"] = Relationship(
        back_populates="avatar", cascade_delete=True)


class AvatarPublic(SQLModel):
    id: uuid.UUID
    name: str
    status: str
    weight_url: Optional[str] = None
    voice_url: Optional[str] = None


class AvatarsPublic(SQLModel):
    data: list[AvatarPublic]
    count: int
