import uuid

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel, Column, Boolean
from sqlalchemy.types import Text


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
    llmodel_responses: list["LLModelResponse"] = Relationship(
        back_populates="owner", cascade_delete=True)


class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    title: str | None = Field(
        default=None, min_length=1, max_length=255)  # type: ignore


class Item(ItemBase, table=True):
    __tablename__ = "item"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


class ChatMessageBase (SQLModel):
    message: str | None = Field(default=None, sa_column=Column(Text))


class ChatMessageCreate (ChatMessageBase):
    pass


class ChatMessageUpdate (ChatMessageBase):
    message: str | None = Field(default=None, sa_column=Column(Text))


class ChatMessage (ChatMessageBase, table=True):
    __tablename__ = "chat_message"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    message: str | None = Field(default=None, sa_column=Column(Text))
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="chat_messages")


class ChatMessagePublic (ChatMessageBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ChatMessagesPublic (SQLModel):
    data: list[ChatMessagePublic]
    count: int


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


class Message(SQLModel):
    message: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
