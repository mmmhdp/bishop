from app.message.Message import Message, MessageCreate
from app.user.User import User
from app.chat.Chat import Chat
from app.avatar.Avatar import Avatar
import uuid
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import func, select


async def create_chat_message( # Used only in tests, mb need to be removed
        *,
        session: AsyncSession,
        item_in: MessageCreate) -> Message:

    db_chat_message = Message.model_validate(item_in)
    session.add(db_chat_message)
    await session.commit()
    await session.refresh(db_chat_message)
    return db_chat_message

async def get_user_messages(
        *,
        session: AsyncSession,
        user: User,
        skip: int = 0,
        limit: int = 100) -> list[Message]:
    
    statement = (
        select(Message)
        .join(Chat, Message.chat_id == Chat.id)
        .join(Avatar, Chat.avatar_id == Avatar.id)
        .join(User, Avatar.user_id == User.id)
        .where(User.id == user.id)
        .offset(skip)
        .limit(limit)
    )
    messages_result = await session.exec(statement)
    messages = messages_result.all()

    return messages

async def get_user_by_message_id(*, session: AsyncSession, message_id: uuid.UUID) -> User:
    statement = (
        select(User)
        .join(Avatar, User.id == Avatar.user_id)
        .join(Chat, Avatar.id == Chat.avatar_id)
        .join(Message, Chat.id == Message.chat_id)
        .where(Message.id == message_id)
    )
    
    result = await session.exec(statement)
    user = result.first()
    
    return user
