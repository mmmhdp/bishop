from typing import Any
import uuid

from fastapi import APIRouter, HTTPException

from app.common.api_deps import (
    SessionDep,
    CurrentUser,
    ProducerDep,
    CacheDep,
)
from app.message.Message import (
    Message,
    MessageCreate,
    MessagePublic,
    MessagesPublic,
    MessageUpdate
)
from app.common.models.SimpleMessage import SimpleMessage
from app.message import message_repository
from app.message import message_broker_service

router = APIRouter()


@router.get("/", response_model=MessagesPublic)
async def read_messages(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    avatar_id: uuid.UUID,
    chat_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve messages for a specific chat.
    """
    messages = await message_repository.get_messages_for_chat(
        session=session, chat_id=chat_id, skip=skip, limit=limit
    )
    return MessagesPublic(data=messages, count=len(messages))


@router.get("/{message_id}", response_model=MessagePublic)
async def read_message(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    message_id: uuid.UUID
) -> Any:
    """
    Get a specific message from a chat.
    """
    message = await session.get(Message, message_id)
    if not message:
        raise HTTPException(
            status_code=404, detail="Message not found")
    return message


@router.post("/", response_model=MessagePublic)
async def create_message(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    avatar_id: uuid.UUID,
    chat_id: uuid.UUID,
    item_in: MessageCreate,
    producer: ProducerDep
) -> Any:
    """
    Create a new message in a specific chat.
    """
    message = Message(
        **item_in.model_dump(),
        id=uuid.uuid4(),
        user_id=current_user.id,
        avatar_id=avatar_id,
        chat_id=chat_id
    )

    session.add(message)
    await session.commit()
    await session.refresh(message)

    await message_broker_service.send_generate_response_message(
        producer=producer,
        message_id=message.id,
        user_message=message.text
    )

    return message


@router.put("/{message_id}", response_model=MessagePublic)
async def update_message(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    message_id: uuid.UUID,
    item_in: MessageUpdate
) -> Any:
    """
    Update a message.
    """
    message = await session.get(Message, message_id)
    if not message:
        raise HTTPException(
            status_code=404, detail="Base message for update is not found")

    update_dict = item_in.model_dump(exclude_unset=True)
    message.sqlmodel_update(update_dict)
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


@router.delete("/{message_id}")
async def delete_message(
    *,
    session: SessionDep,
    message_id: uuid.UUID
) -> SimpleMessage:
    """
    Delete a message.
    """
    message = await session.get(Message, message_id)
    if not message:
        raise HTTPException(
            status_code=404, detail="Message not found")

    await session.delete(message)
    await session.commit()

    return SimpleMessage(message="Message deleted successfully")


@router.get("/{message_id}/response/")
async def get_avatar_response(
    *,
    session: SessionDep,
    chache_db: CacheDep,
    current_user: CurrentUser,
    avatar_id: uuid.UUID,
    chat_id: uuid.UUID,
    message_id: uuid.UUID,
) -> Message:

    rsp_id = await message_repository.get_response_id_by_msg_id(
        chache_db, message_id
    )
    if not rsp_id:
        return HTTPException(status_code=404, detail="Response not found")

    rsp_msg = await session.get(Message, message_id)
    if not rsp_msg:
        raise HTTPException(
            status_code=404, detail="Response not found")

    return rsp_msg
