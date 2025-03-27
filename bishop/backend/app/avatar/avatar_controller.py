import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import col, delete, func, select

from app.user.User import User
from app.common.models.SimpleMessage import SimpleMessage
from app.avatar import avatar_repository
from app.common.api_deps import (
    CurrentUser,
    SessionDep,
    ProducerDep
)
from app.avatar.Avatar import (
    AvatarCreate,
    AvatarUpdate,
    AvatarPublic,
    AvatarsPublic,
    Avatar
)
from app.avatar import avatar_broker_service
router = APIRouter()


@router.get(
    "/",
    response_model=AvatarsPublic,
)
async def read_user_avatars(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve avatars related to the current user.
    """
    # Count avatars belonging to the current user
    count_statement = select(func.count()).select_from(
        Avatar).where(Avatar.user_id == current_user.id)
    count_result = await session.exec(count_statement)
    count = count_result.one()

    # Select avatars with pagination
    statement = (
        select(Avatar)
        .where(Avatar.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    avatars_result = await session.exec(statement)
    avatars = avatars_result.all()

    return AvatarsPublic(data=avatars, count=count)


@router.post("/")
async def create_avatar(*, session: SessionDep, current_user: CurrentUser, avatar_in: AvatarCreate) -> Any:
    """
    Create new avatar.
    """
    new_avatar = await avatar_repository.create_avatar(session=session, avatar_create=avatar_in, user=current_user)

    return {"avatar_id": new_avatar.id}


@router.put("/{id}", response_model=AvatarUpdate)
async def update_avatar(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
        item_in: AvatarUpdate) -> Any:
    """
    Update avatar's name.
    """
    avatar = await session.get(Avatar, id)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    if not current_user.is_superuser and (avatar.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    update_dict = item_in.model_dump(exclude_unset=True)
    avatar.sqlmodel_update(update_dict)
    session.add(avatar)
    await session.commit()
    await session.refresh(avatar)
    return avatar


@router.delete("/{id}")
async def delete_avatar(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> SimpleMessage:
    """
    Delete an message.
    """
    avatar = await session.get(Avatar, id)
    if not avatar:
        raise HTTPException(status_code=404, detail="Message not found")
    if not current_user.is_superuser and (avatar.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    await session.delete(avatar)
    await session.commit()
    return SimpleMessage(message="Avatar deleted successfully")


@router.post("/{id}/train/start")
async def start_training(
    session: SessionDep, current_user: CurrentUser,
    producer: ProducerDep,
    id: uuid.UUID
) -> SimpleMessage:
    """
    Trigger training for a specific avatar.
    """
    avatar = await session.get(Avatar, id)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    if not current_user.is_superuser and avatar.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    await avatar_broker_service.send_train_start_message(
        session=session,
        producer=producer, avatar_id=id)
    return SimpleMessage(message=f"Training started for avatar {id}")


@router.post("/{id}/train/stop")
async def stop_training(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID,
    producer: ProducerDep,
) -> SimpleMessage:
    """
    Stop training for a specific avatar.
    """
    avatar = await session.get(Avatar, id)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    if not current_user.is_superuser and avatar.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    await avatar_broker_service.send_train_stop_message(
        session=session,
        producer=producer, avatar_id=id)
    return SimpleMessage(message=f"Training stop requested for avatar {id}")


@router.get("/{id}/train/status")
async def get_training_status(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID,
    producer: ProducerDep,
) -> dict[str, str]:
    """
    Check training status for a specific avatar (mocked).
    """
    avatar = await session.get(Avatar, id)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    if not current_user.is_superuser and avatar.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # You can later pull this from Redis or a status topic
    return {"status": "training_not_started"}
