import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.user import user_repository
from app.user.User import User
from app.chat import chat_repository
from app.common.api_deps import (
    CurrentUser,
    SessionDep,
)
from app.chat.Chat import (
    ChatCreate,
    Chat
)

router = APIRouter()


@router.post("/")
async def create_chat(*, session: SessionDep, current_user: CurrentUser, chat_in: ChatCreate) -> Any:
    """
    Create new chat.
    """
    # TODO: check if
    # - avatar is created
    # - avatar belongs to current_user 
    # - chat with this avatar wasn't created earlier
    new_chat = await chat_repository.create_chat(session=session, chat_create=chat_in)
    
    return {"chat_id": new_chat.id}