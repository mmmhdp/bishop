import uuid
from typing import Any

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.avatar.Avatar import (
    Avatar, AvatarCreate
)
from app.user.User import User

async def create_avatar(*, session: AsyncSession, avatar_create: AvatarCreate, user: User) -> Avatar:
    db_obj = Avatar(
        user_id=user.id,
        name=avatar_create.name,
        user=user
    )
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj
