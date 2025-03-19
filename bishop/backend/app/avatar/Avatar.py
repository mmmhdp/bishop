import uuid

from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy.types import Text
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.user.User import User

class AvatarBase (SQLModel):
    name: str = Field(sa_column=Column(Text, nullable=False))

class AvatarCreate (AvatarBase):
    pass

class AvatarUpdate (AvatarBase):
    pass

class Avatar (AvatarBase, table=True):
    __tablename__ = "avatar"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    weight_url: str | None = Field(default=None, sa_column=(Text))
    user: Optional["User"] = Relationship(back_populates="avatars")