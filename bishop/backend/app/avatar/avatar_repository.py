import uuid

from fastapi import HTTPException, status
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession


from app.user.User import User
from app.avatar.Avatar import (
    Avatar, AvatarCreate, AvatarUpdate, AvatarsPublic
)

from app.common.api_deps import (
    CurrentUser,
    SessionDep,
    ProducerDep,
)


async def create_avatar(
        *, session: AsyncSession,
        avatar_create: AvatarCreate,
        user: User
) -> Avatar:
    db_obj = Avatar(
        user_id=user.id,
        name=avatar_create.name,
        user=user
    )
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj


async def read_current_user_avatars(
    session: AsyncSession,
    current_user: CurrentUser,
    skip: int,
    limit: int,
) -> AvatarsPublic:
    count_statement = select(func.count()).select_from(
        Avatar).where(Avatar.user_id == current_user.id)
    count_result = await session.exec(count_statement)
    count = count_result.one()

    statement = (
        select(Avatar)
        .where(Avatar.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    avatars_result = await session.exec(statement)
    avatars = avatars_result.all()

    return AvatarsPublic(data=avatars, count=count)


async def read_avatar_by_id(
        session: AsyncSession,
        avatar_id: uuid.UUID
) -> Avatar:
    result = await session.exec(select(Avatar).where(Avatar.id == avatar_id))
    avatar = result.first()
    if not avatar:
        return None
    return avatar


async def read_avatars_for_user(
        session: AsyncSession,
        user_id: uuid.UUID
) -> AvatarsPublic:
    result = await session.exec(select(Avatar).where(Avatar.user_id == user_id))
    return result.all()


async def update_avatar(
        session: AsyncSession,
        avatar_id: uuid.UUID,
        avatar_update: AvatarUpdate
) -> Avatar:
    avatar = await read_avatar_by_id(session, avatar_id)
    if not avatar:
        return None
    avatar.name = avatar_update.name
    await session.commit()
    await session.refresh(avatar)
    return avatar


async def delete_avatar(
        session: AsyncSession,
        avatar_id: uuid.UUID
) -> None:
    avatar = await read_avatar_by_id(session, avatar_id)
    if not avatar:
        return None
    await session.delete(avatar)
    await session.commit()
