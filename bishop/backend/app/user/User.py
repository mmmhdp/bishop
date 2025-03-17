from app.item.Item import Item

from app.chat_message.ChatMessage import ChatMessage
from app.llm_model_response.LLMModelResponse import LLMModelResponse
from app.transcription.Transcription import Transcription

from typing import TYPE_CHECKING
import uuid

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdate(UserBase):
    email: EmailStr | None = Field(
        default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class User(UserBase, table=True):
    __tablename__ = "user"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(
        back_populates="owner", cascade_delete=True)
    chat_messages: list["ChatMessage"] = Relationship(
        back_populates="owner", cascade_delete=True)
    llmmodel_responses: list["LLMModelResponse"] = Relationship(
        back_populates="owner", cascade_delete=True)
    transcriptions: list["Transcription"] = Relationship(
        back_populates="owner", cascade_delete=True)


class UserPublic(UserBase):
    "User Public Interface"
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int
