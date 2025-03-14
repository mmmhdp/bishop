from sqlmodel.ext.asyncio.session import AsyncSession

from app.chat_message import chat_message_repository
from app.chat_message.ChatMessage import ChatMessage, ChatMessageCreate

from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


async def create_random_chat_message(db: AsyncSession) -> ChatMessage:
    user = await create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    message = random_lower_string()
    item_in = ChatMessageCreate(message=message)
    chat_message = await chat_message_repository.create_chat_message(
        session=db,
        item_in=item_in,
        owner_id=owner_id
    )
    return chat_message
