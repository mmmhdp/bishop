from sqlmodel.ext.asyncio.session import AsyncSession

from app.chat import chat_repository
from app.chat.Chat import Chat, ChatCreate

from app.tests.utils.avatar import create_random_avatar
from app.tests.utils.utils import random_lower_string


async def create_random_chat(db: AsyncSession) -> Chat:
    avatar = await create_random_avatar(db=db)

    chat_in = ChatCreate(
        title=random_lower_string(),
    )
    chat = await chat_repository.create_chat(session=db, chat_create=chat_in, avatar_id=avatar.id)

    return chat
