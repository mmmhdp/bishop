import uuid

from fastapi import APIRouter, HTTPException

from app.common.logging_service import logger
from app.common.models.SimpleMessage import SimpleMessage
from app.common.api_deps import (
    CurrentUser,
    SessionDep,
    ProducerDep,
)
from app.avatar.Avatar import (
    AvatarCreate,
    AvatarPublic,
    AvatarUpdate,
    AvatarsPublic,
    Avatar
)
from app.train_material.TrainMaterial import TrainMaterialsPublic
from app.avatar import avatar_broker_service
from app.avatar import avatar_repository

router = APIRouter()

AVATAR_STATUS = {
    "available": "available",
    "training": "training",
    "deleted": "deleted"
}


@router.get("/", response_model=AvatarsPublic)
async def read_user_avatars(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> AvatarsPublic:
    """
    Retrieve avatars related to the current user.
    """
    avatar_list = await avatar_repository.read_current_user_avatars(
        session=session, current_user=current_user, skip=skip, limit=limit
    )
    return avatar_list


@router.get("/{avatar_id}", response_model=AvatarPublic)
async def read_avatar(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    avatar_id: uuid.UUID
) -> Avatar:
    """
    Get a specific avatar by ID.
    """
    avatar = await avatar_repository.read_avatar_by_id(
        session=session, avatar_id=avatar_id
    )
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    if not current_user.is_superuser and (avatar.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    return avatar


@router.post("/", response_model=AvatarPublic)
async def create_avatar(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    avatar_in: AvatarCreate
) -> Avatar:
    """
    Create new avatar.
    """
    new_avatar = await avatar_repository.create_avatar(
        session=session, avatar_create=avatar_in, user=current_user
    )

    await avatar_repository.set_training_status(
        session=session,
        avatar_id=new_avatar.id,
        status=AVATAR_STATUS["available"]
    )

    return new_avatar


@router.put("/{avatar_id}", response_model=AvatarUpdate)
async def update_avatar(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    avatar_id: uuid.UUID,
    item_in: AvatarUpdate
) -> Avatar:
    """
    Update avatar's name.
    """
    avatar = await session.get(Avatar, avatar_id)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    if not current_user.is_superuser and (avatar.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    avatar = await avatar_repository.update_avatar(session, avatar_id, item_in)
    return avatar


@router.delete("/{avatar_id}", response_model=SimpleMessage)
async def delete_avatar(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    avatar_id: uuid.UUID
) -> SimpleMessage:
    """
    Delete an avatar.
    """
    avatar = await session.get(Avatar, avatar_id)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    if not current_user.is_superuser and (avatar.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    await avatar_repository.delete_avatar(
        session=session,
        avatar_id=avatar_id
    )
    return SimpleMessage(message="Avatar deleted successfully")


@router.get("/{avatar_id}/train/materials", response_model=TrainMaterialsPublic)
async def get_current_train_materials(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    avatar_id: uuid.UUID,
) -> TrainMaterialsPublic:
    """
    Get all training materials for a specific avatar, which is in training on pool now.
    """
    avatar = await session.get(Avatar, avatar_id)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    if not current_user.is_superuser and (avatar.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    train_materials = await avatar_repository.get_avaliable_train_materials(
        session=session,
        avatar_id=avatar_id
    )

    print(f"train_materials: {train_materials}")

    return train_materials


@router.post("/{avatar_id}/train/start", response_model=SimpleMessage)
async def start_training(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    producer: ProducerDep,
    avatar_id: uuid.UUID
) -> SimpleMessage:
    """
    Trigger training for a specific avatar.
    """
    avatar = await session.get(Avatar, avatar_id)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    if not current_user.is_superuser and avatar.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    current_status = await avatar_repository.get_training_status(
        session=session,
        avatar_id=avatar_id
    )

    if current_status == AVATAR_STATUS["training"]:
        return SimpleMessage(message=f"Training in process for avatar {avatar_id}")

    await avatar_repository.set_training_status(
        session=session,
        avatar_id=avatar_id,
        status=AVATAR_STATUS["training"]
    )

    await avatar_broker_service.send_train_start_message(
        session=session,
        producer=producer,
        avatar_id=avatar_id
    )

    current_status = await avatar_repository.get_training_status(
        session=session,
        avatar_id=avatar_id
    )
    logger.info("END of training status check for avatar %s: %s",
                avatar_id, current_status)
    return SimpleMessage(message=f"Training started for avatar {avatar_id}")


@router.post("/{avatar_id}/train/stop", response_model=SimpleMessage)
async def stop_training(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    avatar_id: uuid.UUID,
    producer: ProducerDep,
) -> SimpleMessage:
    """
    Stop training for a specific avatar.
    """
    avatar = await session.get(Avatar, avatar_id)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    if not current_user.is_superuser and avatar.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    status = await avatar_repository.get_training_status(
        session=session,
        avatar_id=avatar.id
    )

    if status == AVATAR_STATUS["available"]:
        return SimpleMessage(message=f"Training stop requested for avatar {avatar_id}")

    logger.info(f"Stopping training for avatar {avatar_id}")

    await avatar_broker_service.send_train_stop_message(
        producer=producer,
        avatar_id=avatar_id
    )

    await avatar_repository.set_training_status(
        session=session,
        avatar_id=avatar_id,
        status=AVATAR_STATUS["available"]
    )

    logger.info(f"Training stopped for avatar {avatar_id}")

    return SimpleMessage(message=f"Training stop requested for avatar {avatar_id}")


@router.post("/{avatar_id}/train/status", response_model=SimpleMessage)
async def get_training_status(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    avatar_id: uuid.UUID,
) -> SimpleMessage:
    """
    Get training status for a specific avatar.
    """

    logger.info(f"Checking training status for avatar {avatar_id}")
    status = await avatar_repository.get_training_status(
        session=session,
        avatar_id=avatar_id,
    )

    if status:
        return SimpleMessage(message=status)

    raise HTTPException(status_code=404, detail="Avatar not found")
