import uuid

from sqlmodel import select, func
from typing import Optional

from app.common.logging_service import logger
from app.user.User import User
from app.avatar.Avatar import (
    Avatar, AvatarCreate, AvatarUpdate, AvatarsPublic
)

from app.common.api_deps import (
    CurrentUser,
    SessionDep,
    CacheDep,
)


async def create_avatar(
        *, session: SessionDep,
        avatar_create: AvatarCreate,
        user: User
) -> Avatar:
    logger.info(f"Creating avatar for user {user.id}")
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
    session: SessionDep,
    current_user: CurrentUser,
    skip: int,
    limit: int,
) -> AvatarsPublic:
    logger.info(f"Reading avatars for current user {current_user.id}")
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
        session: SessionDep,
        avatar_id: uuid.UUID
) -> Avatar:
    logger.info(f"Reading avatar {avatar_id}")
    result = await session.exec(select(Avatar).where(Avatar.id == avatar_id))
    avatar = result.first()
    return avatar if avatar else None


async def read_avatars_for_user(
        session: SessionDep,
        user_id: uuid.UUID
) -> AvatarsPublic:
    logger.info(f"Reading avatars for user {user_id}")
    result = await session.exec(select(Avatar).where(Avatar.user_id == user_id))
    return result.all()


async def update_avatar(
        session: SessionDep,
        avatar_id: uuid.UUID,
        avatar_update: AvatarUpdate
) -> Avatar:
    logger.info(f"Updating avatar {avatar_id}")
    avatar = await read_avatar_by_id(session, avatar_id)
    if not avatar:
        return None
    avatar.name = avatar_update.name
    await session.commit()
    await session.refresh(avatar)
    return avatar


async def delete_avatar(
        session: SessionDep,
        cache_db: CacheDep,
        avatar_id: uuid.UUID
) -> None:
    logger.info(f"Deleting avatar {avatar_id}")
    avatar = await read_avatar_by_id(session, avatar_id)
    if not avatar:
        return None

    await session.delete(avatar)
    await session.commit()

    print(cache_db)
    res = await cache_db.delete(str(avatar_id))
    print(res)
    return True


async def get_training_status(
    cache_db: CacheDep,
    avatar_id: uuid.UUID,
) -> Optional[uuid.UUID]:
    logger.info(f"Checking training status for avatar {avatar_id}")
    if await cache_db.exists(str(avatar_id)):
        value = await cache_db.get(str(avatar_id))
        return value
    return None


async def set_training_status(
    cache_db: CacheDep,
    avatar_id: uuid.UUID,
    status: str,
) -> None:
    await cache_db.set(str(avatar_id), status)
    logger.info(f"Set training status for avatar {avatar_id} to {status}")
