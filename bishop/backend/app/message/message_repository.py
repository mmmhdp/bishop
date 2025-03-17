from app.message.Message import Message, MessageCreate
import uuid
from sqlmodel.ext.asyncio.session import AsyncSession


async def create_chat_message( # Used only in tests, mb need to be removed
        *,
        session: AsyncSession,
        item_in: MessageCreate) -> Message:

    db_chat_message = Message.model_validate(item_in)
    session.add(db_chat_message)
    await session.commit()
    await session.refresh(db_chat_message)
    return db_chat_message
