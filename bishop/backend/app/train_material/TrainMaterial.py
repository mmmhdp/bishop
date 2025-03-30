import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy.types import Text, Boolean
from sqlalchemy.sql import func


class TrainMaterialBase(SQLModel):
    title: str = Field(nullable=False)


class TrainMaterialCreate(TrainMaterialBase):
    pass


if TYPE_CHECKING:
    from app.avatar.Avatar import Avatar


class TrainMaterial(TrainMaterialBase, table=True):
    __tablename__ = "train_material"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: Optional[str] = Field(
        sa_column=Column(
            Text, nullable=False,
            default=f"material_{uuid.uuid4()}"
        )
    )
    url: Optional[str] = Field(sa_column=Column(Text, nullable=False))
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

    avatar_id: uuid.UUID = Field(foreign_key="avatar.id", nullable=False)
    avatar: "Avatar" = Relationship(back_populates="train_materials")


class TrainMaterialPublic(SQLModel):
    id: uuid.UUID
    title: str
    weight_url: Optional[str] = None


class TrainMaterialsPublic(SQLModel):
    data: list[TrainMaterial]
    count: int
