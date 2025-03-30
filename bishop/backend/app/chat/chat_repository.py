import uuid
from typing import List, Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.chat.Chat import Chat, ChatCreate, ChatUpdate


async def create_chat(
        *, session: AsyncSession,
        chat_create: ChatCreate,
        avatar_id: uuid.UUID
) -> Chat:
    db_obj = Chat(
        avatar_id=avatar_id,
        title=chat_create.title
    )
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj


async def is_chat_exists_for_avatar(
    *,
    session: AsyncSession,
    avatar_id: uuid.UUID,
    chat_create: ChatCreate
) -> Optional[Chat]:
    statement = select(Chat).where(
        Chat.avatar_id == avatar_id,
        Chat.title == chat_create.title
    )
    chat_result = await session.exec(statement)
    return chat_result.first()


async def get_chat_by_id(
    *,
    session: AsyncSession,
    chat_id: uuid.UUID
) -> Optional[Chat]:
    return await session.get(Chat, chat_id)


async def get_chats_for_avatar(
    *,
    session: AsyncSession,
    avatar_id: uuid.UUID
) -> List[Chat]:
    statement = select(Chat).where(Chat.avatar_id == avatar_id)
    result = await session.exec(statement)
    return result.all()


async def update_chat(
    *,
    session: AsyncSession,
    chat_id: uuid.UUID,
    chat_update: ChatUpdate
) -> Optional[Chat]:
    db_chat = await session.get(Chat, chat_id)
    if not db_chat:
        return None
    for key, value in chat_update.dict(exclude_unset=True).items():
        setattr(db_chat, key, value)
    session.add(db_chat)
    await session.commit()
    await session.refresh(db_chat)
    return db_chat


async def delete_chat(
    *,
    session: AsyncSession,
    chat_id: uuid.UUID
) -> bool:
    db_chat = await session.get(Chat, chat_id)
    if not db_chat:
        return False
    await session.delete(db_chat)
    await session.commit()
    return True
