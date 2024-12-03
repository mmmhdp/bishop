import uuid

from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy.types import Text
from app.models.User import User


class LLModelResponseBase (SQLModel):
    response: str | None = Field(default=None, sa_column=Column(Text))
    answer_to_msg_with_id: uuid.UUID | None = Field(default=None)


class LLModelResponseCreate (LLModelResponseBase):
    pass


class LLModelResponseUpdate (LLModelResponseBase):
    response: str | None = Field(default=None, sa_column=Column(Text))


class LLModelResponse (LLModelResponseBase, table=True):
    __tablename__ = "llmodel_response"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    response: str | None = Field(default=None, sa_column=Column(Text))
    answer_to_msg_with_id: uuid.UUID = Field(
        foreign_key="chat_message.id",
        default=None
    )

    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="llmodel_responses")


class LLModelResponsePublic (LLModelResponseBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class LLModelResponsesPublic (SQLModel):
    data: list[LLModelResponsePublic]
    count: int
