import uuid

from sqlmodel import select, func
from typing import Optional

from app.common.logging_service import logger
from app.user.User import User
from app.avatar.Avatar import (
    Avatar,
    AvatarCreate,
    AvatarUpdate,
    AvatarsPublic
)
from app.train_material.TrainMaterial import TrainMaterialsPublic, TrainMaterial

from app.common.api_deps import (
    CurrentUser,
    SessionDep,
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
        user=user,
        status="available",
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
        avatar_id: uuid.UUID
) -> None:
    logger.info(f"Deleting avatar {avatar_id}")
    avatar = await read_avatar_by_id(session, avatar_id)
    if not avatar:
        return None

    await session.delete(avatar)
    await session.commit()
    return True


async def set_training_status(
    session: SessionDep,
    avatar_id: uuid.UUID,
    status: str,
) -> None:
    logger.info(f"Setting training status for avatar {avatar_id} to {status}")
    result = await session.exec(select(Avatar).where(Avatar.id == avatar_id))
    avatar = result.first()
    if not avatar:
        logger.error(f"Avatar {avatar_id} not found")
        return None
    avatar.status = status
    await session.commit()
    await session.refresh(avatar)


async def get_training_status(
    session: SessionDep,
    avatar_id: uuid.UUID,
) -> Optional[str]:
    logger.info(f"Getting training status for avatar {avatar_id}")
    result = await session.exec(select(Avatar.status).where(Avatar.id == avatar_id))
    status = result.first()
    if not status:
        logger.error(f"Avatar {avatar_id} not found")
        return None
    logger.info(f"Status for avatar {avatar_id} is {status}")
    return status


async def get_avaliable_train_materials(
    session: SessionDep,
    avatar_id: uuid.UUID,
) -> TrainMaterialsPublic:
    logger.info(f"Getting available training materials for avatar {avatar_id}")
    statement = select(TrainMaterial).where(
        TrainMaterial.avatar_id == avatar_id,
        TrainMaterial.is_trained_on == False
    )

    result = await session.exec(statement)
    untrained_materials = result.all()

    materials_data = [
        {
            "id": str(material.id),
            "type": material.type,
            "url": material.url
        }
        for material in untrained_materials
    ]
    return TrainMaterialsPublic(data=materials_data, count=len(materials_data))


async def invalidate_train_materials(
    session: SessionDep,
    avatar_id: uuid.UUID,
):
    materials = await get_avaliable_train_materials(
        session=session,
        avatar_id=avatar_id
    )

    for material in materials.data:
        db_material = await session.get(TrainMaterial, material.id)
        if db_material is not None:
            db_material.is_trained_on = True
            await session.commit()
            await session.refresh(db_material)

    logger.info(f"Invalidated training materials for avatar {avatar_id}")
    return materials


async def update_avatar_voice_url(
    session: SessionDep,
    avatar_id: uuid.UUID,
    voice_url: str
) -> Optional[Avatar]:
    logger.info(f"Updating voice_url for avatar {avatar_id} to {voice_url}")

    avatar = await read_avatar_by_id(session, avatar_id)
    if not avatar:
        logger.error(f"Avatar {avatar_id} not found")
        return None

    avatar.voice_url = voice_url
    await session.commit()
    await session.refresh(avatar)
    return avatar
