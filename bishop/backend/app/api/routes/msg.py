import logging
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models.ChatMessage import (
    ChatMessage,
    ChatMessageCreate,
    ChatMessagePublic,
    ChatMessagesPublic,
    ChatMessageUpdate,
)
from app.models.Mixin import (
    Message
)

router = APIRouter()


@router.get("/hello/", response_model=Message)
async def hello(
) -> Any:
    return Message(message="Hello")


@router.get("/", response_model=ChatMessagesPublic)
async def read_messages(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve messages.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(ChatMessage)
        messages_statement = select(ChatMessage).offset(skip).limit(limit)
    else:
        count_statement = (
            select(func.count())
            .select_from(ChatMessage)
            .where(ChatMessage.owner_id == current_user.id)
        )
        messages_statement = (
            select(ChatMessage)
            .where(ChatMessage.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )

    count_result = await session.exec(count_statement)
    count = count_result.one()

    messages_result = await session.exec(messages_statement)
    messages = messages_result.all()

    return ChatMessagesPublic(data=messages, count=count)


@router.get("/{id}", response_model=ChatMessagePublic)
async def read_message(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get message by ID.
    """
    message = await session.get(ChatMessage, id)
    if not message:
        raise HTTPException(status_code=404, detail="ChatMessage not found")
    if not current_user.is_superuser and (message.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return message


@router.post("/", response_model=ChatMessagePublic)
async def create_message(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    item_in: ChatMessageCreate
) -> Any:
    """
    Create new message.
    """
    message = ChatMessage.model_validate(
        item_in, update={"owner_id": current_user.id})
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


@router.put("/{id}", response_model=ChatMessagePublic)
async def update_message(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: ChatMessageUpdate,
) -> Any:
    """
    Update an message.
    """
    message = await session.get(ChatMessage, id)
    if not message:
        raise HTTPException(status_code=404, detail="ChatMessage not found")
    if not current_user.is_superuser and (message.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = item_in.model_dump(exclude_unset=True)
    message.sqlmodel_update(update_dict)
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


@router.delete("/{id}")
async def delete_message(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an message.
    """
    message = await session.get(ChatMessage, id)
    if not message:
        raise HTTPException(status_code=404, detail="ChatMessage not found")
    if not current_user.is_superuser and (message.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    await session.delete(message)
    await session.commit()
    return Message(message="ChatMessage deleted successfully")
