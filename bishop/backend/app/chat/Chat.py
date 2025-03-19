import uuid

from sqlmodel import Field, Relationship, SQLModel, Column

from app.message.Message import Message

class ChatBase (SQLModel):
    avatar_id: uuid.UUID = Field(
        foreign_key="avatar.id", nullable=False, ondelete="CASCADE"
    )

class ChatCreate (ChatBase):
    pass

class Chat (ChatBase, table=True):
    __tablename__ = "chat"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    # TODO: messages: list["Message"] = Relationship(back_populates="chat", cascade_delete=True)
