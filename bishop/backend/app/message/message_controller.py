import logging
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.common.api_deps import CurrentUser, SessionDep

from app.message.Message import (
    Message,
    MessageCreate,
    MessagePublic,
    MessagesPublic,
    MessageUpdate,
)

from app.common.models.SimpleMessage import SimpleMessage
from app.message.message_repository import get_user_messages, get_user_by_message_id

router = APIRouter()


@router.get("/hello/", response_model=SimpleMessage)
async def hello(
) -> Any:
    return SimpleMessage(message="Hello")


@router.get("/", response_model=MessagesPublic)
async def read_messages(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve messages.
    """
    if current_user.is_superuser:
        messages_statement = select(Message).offset(skip).limit(limit)
        messages_result = await session.exec(messages_statement)
        messages = messages_result.all()
    else:
        messages = await get_user_messages(session=session, user=current_user, skip=skip, limit=limit)
        
    count = len(messages)

    return MessagesPublic(data=messages, count=count)


@router.get("/{id}", response_model=MessagePublic)
async def read_message(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get message by ID.
    """
    message = await session.get(Message, id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    if not current_user.is_superuser:
         message_user = await get_user_by_message_id(session=session, message_id=id)
         if not message_user:
             raise HTTPException(status_code=500, detail="User for this message not found, logic error")
         if message_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Not enough permissions")

    return message


@router.post("/", response_model=MessagePublic)
async def create_message(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    item_in: MessageCreate
) -> Any:
    """
    Create new message.
    """
    message = Message.model_validate(item_in)
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


@router.put("/{id}", response_model=MessagePublic)
async def update_message(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: MessageUpdate,
) -> Any:
    """
    Update an message.
    """
    message = await session.get(Message, id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    if not current_user.is_superuser:
        message_user = await get_user_by_message_id(session=session, message_id=id)
        if not message_user:
            raise HTTPException(status_code=500, detail="User for this message not found, logic error")
        if message_user.id != current_user.id:
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
) -> SimpleMessage:
    """
    Delete an message.
    """
    message = await session.get(Message, id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    if not current_user.is_superuser:
        message_user = await get_user_by_message_id(session=session, message_id=id)
        if not message_user:
            raise HTTPException(status_code=500, detail="User for this message not found, logic error")
        if message_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Not enough permissions")
        
    await session.delete(message)
    await session.commit()
    return SimpleMessage(message="Message deleted successfully")
