import uuid
from enum import Enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy.types import Text, Boolean, Enum as SQLAlchemyEnum
from sqlalchemy.sql import func


class SourceType(str, Enum):
    AUDIO = "audio"
    VIDEO = "video"
    TXT = "txt"


class TrainMaterialBase(SQLModel):
    avatar_id: uuid.UUID = Field(foreign_key="avatar.id", nullable=False)


class TrainMaterialCreate(TrainMaterialBase):
    type: SourceType


if TYPE_CHECKING:
    from app.avatar.Avatar import Avatar


class TrainMaterial(TrainMaterialBase, table=True):
    __tablename__ = "train_material"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    type: SourceType = Field(
        sa_column=Column(SQLAlchemyEnum(SourceType), nullable=False)
    )
    url: str = Field(sa_column=Column(Text, nullable=False))
    is_trained_on: bool = Field(sa_column=Column(
        Boolean, nullable=False, default=False))
    created_at: datetime = Field(
        sa_column=Column(
            Text, nullable=False, server_default=func.now()
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            Text, nullable=False, server_default=func.now(), onupdate=func.now()
        )
    )
    avatar: "Avatar" = Relationship(back_populates="train_materials")
