import uuid

from sqlmodel import select
from app.message.Message import Message, MessagesPublic

from app.common.api_deps import SessionDep, CacheDep


async def get_messages_for_chat(
    *,
    session: SessionDep,
    chat_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100
) -> MessagesPublic:
    statement = (
        select(Message)
        .where(Message.chat_id == chat_id)
        .offset(skip)
        .limit(limit)
    )
    result = await session.exec(statement)
    return result.all()


async def get_response_id_by_msg_id(
    cache_db: CacheDep,
    message_id: uuid.UUID
) -> uuid.UUID:
    response_id = await cache_db.get(f"msg:{message_id}")
    if response_id is None:
        return None

    return uuid.UUID(response_id)
