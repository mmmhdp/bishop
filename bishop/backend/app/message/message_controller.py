from typing import Any, Optional
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
    message, rsp_msg = await message_repository.create_message(
        session=session,
        current_user=current_user,
        avatar_id=avatar_id,
        chat_id=chat_id,
        item_in=item_in
    )

    await message_broker_service.send_generate_response_message(
        producer=producer,
        message_id=rsp_msg.id,
        user_message=message.text
    )

    return rsp_msg


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


@router.get("/{rsp_msg_id}/response/")
async def get_avatar_response(
    *,
    session: SessionDep,
    chache_db: CacheDep,
    current_user: CurrentUser,
    avatar_id: uuid.UUID,
    chat_id: uuid.UUID,
    rsp_msg_id: uuid.UUID,
) -> Message:

    rsp_msg = await session.get(Message, rsp_msg_id)
    if not rsp_msg:
        raise HTTPException(
            status_code=422, detail="Response message is not exists")

    if not rsp_msg.text:
        raise HTTPException(
            status_code=404, detail="Response is not ready yet")

    return rsp_msg
