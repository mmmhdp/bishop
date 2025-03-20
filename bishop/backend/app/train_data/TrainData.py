import uuid
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy.types import Text, Boolean

from app.user.User import User
    

class SourceType(Enum):
    AUDIO = "audio"
    VIDEO = "video"
    TXT = "txt"

class TrainDataBase (SQLModel):
    avatar_id: uuid.UUID = Field(
        foreign_key="avatar.id", nullable=False, ondelete="CASCADE"
    )

class TrainDataCreate(TrainDataBase):
    pass


class TrainData (TrainDataBase, table=True):
    __tablename__ = "train_data"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    type: SourceType = Field(nullable=False)
    url: str = Field(sa_column=Column(Text, nullable=False))
    is_trained_on: bool = Field(sa_column=Column(Boolean, nullable=False, default=False))
    