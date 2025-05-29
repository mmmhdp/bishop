from fastapi import APIRouter, HTTPException
from typing import List
import uuid

from app.chat import chat_repository
from app.chat.Chat import ChatCreate, Chat, ChatUpdate
from app.common.api_deps import CurrentUser, SessionDep

router = APIRouter()


@router.post("/")
async def create_chat(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    avatar_id: uuid.UUID,
    chat_in: ChatCreate
):
    chat = await chat_repository.is_chat_exists_for_avatar(
        session=session, avatar_id=avatar_id, chat_create=chat_in
    )
    if chat:
        raise HTTPException(
            status_code=400,
            detail="The chat with this title already exists for that avatar"
        )
    new_chat = await chat_repository.create_chat(
        session=session,
        chat_create=chat_in,
        avatar_id=avatar_id
    )
    return {"chat_id": new_chat.id}


@router.get("/", response_model=List[Chat])
async def get_chats_for_avatar(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    avatar_id: uuid.UUID
):
    return await chat_repository.get_chats_for_avatar(session=session, avatar_id=avatar_id)


@router.get("/{chat_id}", response_model=Chat)
async def get_chat_by_id(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    chat_id: uuid.UUID
):
    chat = await chat_repository.get_chat_by_id(session=session, chat_id=chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.put("/{chat_id}", response_model=Chat)
async def update_chat(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    chat_id: uuid.UUID,
    chat_update: ChatUpdate
):
    chat = await chat_repository.update_chat(
        session=session, chat_id=chat_id, chat_update=chat_update
    )
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.delete("/{chat_id}")
async def delete_chat(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    chat_id: uuid.UUID
):
    success = await chat_repository.delete_chat(session=session, chat_id=chat_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"ok": True}
