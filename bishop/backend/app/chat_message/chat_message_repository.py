from app.chat_message.ChatMessage import ChatMessage, ChatMessageCreate
import uuid
from sqlmodel.ext.asyncio.session import AsyncSession


async def create_chat_message(
        *,
        session: AsyncSession,
        item_in: ChatMessageCreate,
        owner_id: uuid.UUID) -> ChatMessage:

    db_chat_message = ChatMessage.model_validate(
        item_in, update={"owner_id": owner_id})
    session.add(db_chat_message)
    await session.commit()
    await session.refresh(db_chat_message)
    return db_chat_message
