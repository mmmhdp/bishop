import uuid

from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy.types import Text

from typing import TYPE_CHECKING, Optional


class LLMModelResponseBase (SQLModel):
    response: str | None = Field(default=None, sa_column=Column(Text))
    answer_to_msg_with_id: uuid.UUID | None = Field(default=None)


class LLMModelResponseCreate (LLMModelResponseBase):
    pass


class LLMModelResponseUpdate (LLMModelResponseBase):
    response: str | None = Field(default=None, sa_column=Column(Text))


if TYPE_CHECKING:
    from app.user.User import User


class LLMModelResponse (LLMModelResponseBase, table=True):
    __tablename__ = "llmmodel_response"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    response: str | None = Field(default=None, sa_column=Column(Text))
    answer_to_msg_with_id: uuid.UUID = Field(
        foreign_key="chat_message.id",
        default=None
    )

    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: Optional["User"] = Relationship(back_populates="llmmodel_responses")


class LLMModelResponsePublic (LLMModelResponseBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class LLMModelResponsesPublic (SQLModel):
    data: list[LLMModelResponsePublic]
    count: int
