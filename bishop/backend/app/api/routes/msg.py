import logging
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    ChatMessage,
    ChatMessageCreate,
    ChatMessagePublic,
    ChatMessagesPublic,
    ChatMessageUpdate,
    Message
)

router = APIRouter()


@router.get("/", response_model=ChatMessagesPublic)
def read_messages(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve messages.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(ChatMessage)
        count = session.exec(count_statement).one()
        statement = select(ChatMessage).offset(skip).limit(limit)
        messages = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(ChatMessage)
            .where(ChatMessage.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(ChatMessage)
            .where(ChatMessage.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        messages = session.exec(statement).all()

    return ChatMessagesPublic(data=messages, count=count)


@router.get("/{id}", response_model=ChatMessagePublic)
def read_message(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get message by ID.
    """
    message = session.get(ChatMessage, id)
    if not message:
        raise HTTPException(status_code=404, detail="ChatMessage not found")
    if not current_user.is_superuser and (message.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return message


@router.post("/", response_model=ChatMessagePublic)
def create_message(
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
    session.commit()
    session.refresh(message)
    return message


@router.put("/{id}", response_model=ChatMessagePublic)
def update_message(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: ChatMessageUpdate,
) -> Any:
    """
    Update an message.
    """
    message = session.get(ChatMessage, id)
    if not message:
        raise HTTPException(status_code=404, detail="ChatMessage not found")
    if not current_user.is_superuser and (message.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = item_in.model_dump(exclude_unset=True)
    message.sqlmodel_update(update_dict)
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


@router.delete("/{id}")
def delete_message(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an message.
    """
    message = session.get(ChatMessage, id)
    if not message:
        raise HTTPException(status_code=404, detail="ChatMessage not found")
    if not current_user.is_superuser and (message.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(message)
    session.commit()
    return Message(message="ChatMessage deleted successfully")
