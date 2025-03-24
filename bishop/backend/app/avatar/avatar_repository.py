import uuid
from typing import Any

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.avatar.Avatar import (
    Avatar, AvatarCreate
)
from app.user.User import User


from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status

from app.avatar.Avatar import Avatar, AvatarCreate, AvatarUpdate
from app.user.User import User
import uuid


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


async def read_avatar_by_id(session: AsyncSession, avatar_id: uuid.UUID) -> Avatar:
    result = await session.exec(select(Avatar).where(Avatar.id == avatar_id))
    avatar = result.first()
    if not avatar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")
    return avatar


async def read_avatars_for_user(session: AsyncSession, user_id: uuid.UUID) -> list[Avatar]:
    result = await session.exec(select(Avatar).where(Avatar.user_id == user_id))
    return result.all()


async def update_avatar(session: AsyncSession, avatar_id: uuid.UUID, avatar_update: AvatarUpdate) -> Avatar:
    avatar = await read_avatar_by_id(session, avatar_id)
    avatar.name = avatar_update.name
    await session.commit()
    await session.refresh(avatar)
    return avatar


async def delete_avatar(session: AsyncSession, avatar_id: uuid.UUID) -> None:
    avatar = await read_avatar_by_id(session, avatar_id)
    await session.delete(avatar)
    await session.commit()
