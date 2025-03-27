from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.message.Message import Message
import uuid
from fastapi import HTTPException
from app.common.api_deps import SessionDep, CurrentUser


async def get_messages_for_chat(
    *,
    session: AsyncSession,
    chat_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100
) -> list[Message]:
    statement = (
        select(Message)
        .where(Message.chat_id == chat_id)
        .offset(skip)
        .limit(limit)
    )
    result = await session.exec(statement)
    return result.all()


async def validate_chat_belongs_to_avatar(
        session: SessionDep,
        avatar_id: uuid.UUID, chat_id: uuid.UUID, current_user: CurrentUser):
    from app.chat.Chat import Chat
    from app.avatar.Avatar import Avatar

    chat = await session.get(Chat, chat_id)
    if not chat or chat.avatar_id != avatar_id:
        raise HTTPException(
            status_code=404, detail="Chat does not belong to this avatar")

    if not current_user.is_superuser:
        avatar = await session.get(Avatar, avatar_id)
        if not avatar or avatar.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Not enough permissions")
