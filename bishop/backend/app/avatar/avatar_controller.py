import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.user.User import User
from app.avatar import avatar_repository
from app.common.api_deps import (
    CurrentUser,
    SessionDep
)
from app.avatar.Avatar import (
    AvatarCreate,
    Avatar
)

router = APIRouter()


@router.post("/")
async def create_avatar(*, session: SessionDep, current_user: CurrentUser, avatar_in: AvatarCreate) -> Any:
    """
    Create new avatar.
    """
    new_avatar = await avatar_repository.create_avatar(session=session, avatar_create=avatar_in, user=current_user)
    
    return {"avatar_id": new_avatar.id}