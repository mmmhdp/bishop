import uuid
from typing import Any

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.chat.Chat import (
    Chat, ChatCreate
)


async def create_chat(*, session: AsyncSession, chat_create: ChatCreate) -> Chat:
    db_obj = Chat(
        avatar_id=chat_create.avatar_id
    )
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj
