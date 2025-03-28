from fastapi import APIRouter, HTTPException
from sqlmodel import select
from typing import Any, List
import uuid

from app.common.api_deps import SessionDep, CurrentUser, ProducerDep, MessageGenerationConsumerDep
from app.message.Message import Message, MessageCreate, MessagePublic, MessagesPublic, MessageUpdate
from app.common.models.SimpleMessage import SimpleMessage
from app.message import message_repository
from app.message import message_broker_service
from app.chat import chat_repository
from app.avatar import avatar_repository  # if you have this

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
    await avatar_repository.validate_chat_belongs_to_avatar(
        session, avatar_id, chat_id, current_user)

    messages = await message_repository.get_messages_for_chat(
        session=session, chat_id=chat_id, skip=skip, limit=limit
    )
    return MessagesPublic(data=messages, count=len(messages))


@router.get("/{message_id}", response_model=MessagePublic)
async def read_message(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    avatar_id: uuid.UUID,
    chat_id: uuid.UUID,
    message_id: uuid.UUID
) -> Any:
    """
    Get a specific message from a chat.
    """
    await avatar_repository.validate_chat_belongs_to_avatar(
        session, avatar_id, chat_id, current_user)

    message = await session.get(Message, message_id)
    if not message or message.chat_id != chat_id:
        raise HTTPException(
            status_code=404, detail="Message not found in this chat")
    return message


@router.post("/", response_model=MessagePublic)
async def create_message(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    avatar_id: uuid.UUID,
    chat_id: uuid.UUID,
    item_in: MessageCreate,
    producer: ProducerDep,
    consumer: MessageGenerationConsumerDep
) -> Any:
    """
    Create a new message in a specific chat.
    """
    await avatar_repository.validate_chat_belongs_to_avatar(
        session, avatar_id, chat_id, current_user)

    if item_in.chat_id != chat_id:
        raise HTTPException(status_code=400, detail="Chat ID mismatch")

    message = Message.model_validate(item_in)
    session.add(message)
    await session.commit()
    await session.refresh(message)

    message_broker_service.send_generate_response_message(
        producer=producer,
        message_id=message.id,
        user_message=message.text
    )

    return message


@ router.put("/{message_id}", response_model=MessagePublic)
async def update_message(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    avatar_id: uuid.UUID,
    chat_id: uuid.UUID,
    message_id: uuid.UUID,
    item_in: MessageUpdate
) -> Any:
    """
    Update a message in a specific chat.
    """
    await avatar_repository.validate_chat_belongs_to_avatar(
        session, avatar_id, chat_id, current_user)

    message = await session.get(Message, message_id)
    if not message or message.chat_id != chat_id:
        raise HTTPException(
            status_code=404, detail="Message not found in this chat")

    update_dict = item_in.model_dump(exclude_unset=True)
    message.sqlmodel_update(update_dict)
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


@ router.delete("/{message_id}")
async def delete_message(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    avatar_id: uuid.UUID,
    chat_id: uuid.UUID,
    message_id: uuid.UUID
) -> SimpleMessage:
    """
    Delete a message from a chat.
    """
    await avatar_repository.validate_chat_belongs_to_avatar(
        session, avatar_id, chat_id, current_user)

    message = await session.get(Message, message_id)
    if not message or message.chat_id != chat_id:
        raise HTTPException(
            status_code=404, detail="Message not found in this chat")

    await session.delete(message)
    await session.commit()
    return SimpleMessage(message="Message deleted successfully")
