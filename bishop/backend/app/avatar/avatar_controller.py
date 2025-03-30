import uuid

from fastapi import APIRouter, HTTPException

from app.common.models.SimpleMessage import SimpleMessage
from app.common.api_deps import (
    CurrentUser,
    SessionDep,
    ProducerDep
)
from app.avatar.Avatar import (
    AvatarCreate,
    AvatarPublic,
    AvatarUpdate,
    AvatarsPublic,
    Avatar
)
from app.avatar import avatar_broker_service
from app.avatar import avatar_repository

router = APIRouter()


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
    return new_avatar


@router.put("/{id}", response_model=AvatarUpdate)
async def update_avatar(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: AvatarUpdate
) -> Avatar:
    """
    Update avatar's name.
    """
    avatar = await session.get(Avatar, id)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    if not current_user.is_superuser and (avatar.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    avatar = await avatar_repository.update_avatar(session, id, item_in)
    return avatar


@router.delete("/{id}", response_model=SimpleMessage)
async def delete_avatar(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID
) -> SimpleMessage:
    """
    Delete an message.
    """
    avatar = await session.get(Avatar, id)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    if not current_user.is_superuser and (avatar.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    await avatar_repository.delete_avatar(session, id)
    return SimpleMessage(message="Avatar deleted successfully")


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

    await avatar_broker_service.send_train_start_message(
        session=session,
        producer=producer,
        avatar_id=avatar_id
    )
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

    await avatar_broker_service.send_train_stop_message(
        producer=producer,
        avatar_id=avatar_id
    )
    return SimpleMessage(message=f"Training stop requested for avatar {avatar_id}")
