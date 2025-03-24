from sqlmodel.ext.asyncio.session import AsyncSession

from app.message import message_repository
from app.message.Message import Message, MessageCreate

from app.tests.utils.chat import create_random_chat
from app.tests.utils.utils import random_lower_string


async def create_random_chat_message(db: AsyncSession) -> Message:
    chat = await create_random_chat(db=db)

    item_in = MessageCreate(text=random_lower_string(), chat_id=chat.id)
    chat_message = await message_repository.create_chat_message(session=db, item_in=item_in)
    
    return chat_message
