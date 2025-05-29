import uuid
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, SQLModel, Relationship, Column, ForeignKey
from sqlalchemy.types import Text, Boolean


class TRAINIGN_MATERIAL_TYPE(str, Enum):
    basic = "basic"
    voice_syntesis = "voice_syntesis"


class TrainMaterialBase(SQLModel):
    type: TRAINIGN_MATERIAL_TYPE


class TrainMaterialCreate(TrainMaterialBase):
    pass


if TYPE_CHECKING:
    from app.avatar.Avatar import Avatar


class TrainMaterial(TrainMaterialBase, table=True):
    __tablename__ = "train_material"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    url: Optional[str] = Field(sa_column=Column(Text, nullable=False))
    is_trained_on: bool = Field(sa_column=Column(
        Boolean, nullable=False, default=False))

    type: str = Field(
        sa_column=Column(Text, nullable=False))

    avatar_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey(
            "avatar.id", ondelete="CASCADE"), nullable=False)
    )
    avatar: "Avatar" = Relationship(back_populates="train_materials")


class TrainMaterialPublic(SQLModel):
    id: uuid.UUID
    title: str
    url: Optional[str] = None


class TrainMaterialsPublic(SQLModel):
    data: list[TrainMaterial]
    count: int
