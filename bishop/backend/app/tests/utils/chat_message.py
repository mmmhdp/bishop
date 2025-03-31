from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.chat.Chat import Chat
from app.avatar.Avatar import Avatar
from app.message import message_repository
from app.message.Message import Message, MessageCreate

from app.tests.utils.chat import create_random_chat
from app.tests.utils.utils import random_lower_string


async def create_random_chat_message(
    db: AsyncSession,
) -> Message:
    chat = await create_random_chat(db=db)

    result = await db.exec(
        select(Chat)
        .options(selectinload(Chat.avatar).selectinload(Avatar.user))
        .where(Chat.id == chat.id)
    )
    chat_with_preloads = result.scalar_one()

    item_in = MessageCreate(text=random_lower_string())
    new_message = await message_repository.create_message(
        session=db,
        current_user=chat_with_preloads.avatar.user,
        avatar_id=chat_with_preloads.avatar.id,
        chat_id=chat.id,
        item_in=item_in
    )

    return new_message
