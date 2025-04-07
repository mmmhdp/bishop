import uuid

from sqlmodel import select
from app.message.Message import Message, MessagesPublic, MessageCreate

from app.common.api_deps import SessionDep, CacheDep, CurrentUser


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
    response_id = await cache_db.get(str(message_id))
    return uuid.UUID(response_id) if response_id else None


async def create_message(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    avatar_id: uuid.UUID,
    chat_id: uuid.UUID,
    item_in: MessageCreate,
) -> Message:
    message = Message(
        **item_in.model_dump(),
        id=uuid.uuid4(),
        user_id=current_user.id,
        avatar_id=avatar_id,
        chat_id=chat_id
    )

    rsp_msg_box = Message(
        id=uuid.uuid4(),
        user_id=current_user.id,
        avatar_id=avatar_id,
        chat_id=chat_id,
        text=None,
        is_generated=True,
        dub_url=None,
    )

    session.add(message)
    session.add(rsp_msg_box)

    await session.commit()
    await session.refresh(message)
    await session.refresh(rsp_msg_box)

    return message, rsp_msg_box
