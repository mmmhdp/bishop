from uuid import uuid4
import pytest
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.avatar import avatar_repository
from app.avatar.Avatar import Avatar, AvatarCreate, AvatarUpdate
from app.tests.utils.utils import random_lower_string
from app.tests.utils.user import create_random_user


@pytest.mark.asyncio
async def test_create_avatar(db: AsyncSession):
    user = await create_random_user(db)
    avatar_in = AvatarCreate(name=random_lower_string())
    avatar = await avatar_repository.create_avatar(session=db, avatar_create=avatar_in, user=user)

    assert avatar.id is not None
    assert avatar.name == avatar_in.name
    assert avatar.user_id == user.id


@pytest.mark.asyncio
async def test_read_current_user_avatars(db: AsyncSession):
    user = await create_random_user(db)
    avatar1 = await avatar_repository.create_avatar(
        session=db, avatar_create=AvatarCreate(name="Avatar One"), user=user
    )
    avatar2 = await avatar_repository.create_avatar(
        session=db, avatar_create=AvatarCreate(name="Avatar Two"), user=user
    )

    result = await avatar_repository.read_current_user_avatars(
        session=db, current_user=user, skip=0, limit=10
    )

    assert result.count >= 2
    assert any(a.name == "Avatar One" for a in result.data)
    assert any(a.name == "Avatar Two" for a in result.data)


@pytest.mark.asyncio
async def test_read_avatar_by_id(db: AsyncSession):
    user = await create_random_user(db)
    avatar = await avatar_repository.create_avatar(
        session=db, avatar_create=AvatarCreate(name="Find Me"), user=user
    )

    fetched = await avatar_repository.read_avatar_by_id(session=db, avatar_id=avatar.id)
    assert fetched
    assert fetched.id == avatar.id


@pytest.mark.asyncio
async def test_read_avatars_for_user(db: AsyncSession):
    user = await create_random_user(db)
    await avatar_repository.create_avatar(session=db, avatar_create=AvatarCreate(name="One"), user=user)
    await avatar_repository.create_avatar(session=db, avatar_create=AvatarCreate(name="Two"), user=user)

    avatars = await avatar_repository.read_avatars_for_user(session=db, user_id=user.id)
    assert len(avatars) >= 2


@pytest.mark.asyncio
async def test_update_avatar(db: AsyncSession):
    user = await create_random_user(db)
    avatar = await avatar_repository.create_avatar(
        session=db, avatar_create=AvatarCreate(name="Old Name"), user=user
    )
    updated = await avatar_repository.update_avatar(
        session=db,
        avatar_id=avatar.id,
        avatar_update=AvatarUpdate(name="New Name")
    )

    assert updated.name == "New Name"


@pytest.mark.asyncio
async def test_delete_avatar(
    db: AsyncSession,
):
    user = await create_random_user(db)
    avatar = await avatar_repository.create_avatar(
        session=db, avatar_create=AvatarCreate(name="Delete Me"), user=user
    )

    deleted = await avatar_repository.delete_avatar(
        session=db,
        avatar_id=avatar.id
    )
    assert deleted is True

    result = await db.exec(select(Avatar).where(Avatar.id == avatar.id))
    assert result.first() is None


@pytest.mark.asyncio
async def test_delete_nonexistent_avatar(
    db: AsyncSession,
):
    result = await avatar_repository.delete_avatar(
        session=db,
        avatar_id=uuid4()
    )
    assert result is None


@pytest.mark.asyncio
async def test_update_nonexistent_avatar(db: AsyncSession):
    result = await avatar_repository.update_avatar(
        session=db,
        avatar_id=uuid4(),
        avatar_update=AvatarUpdate(name="Nope")
    )
    assert result is None


@pytest.mark.asyncio
async def test_set_and_get_training_status(db: AsyncSession):
    user = await create_random_user(db)
    avatar = await avatar_repository.create_avatar(
        session=db,
        avatar_create=AvatarCreate(name="Trainer"),
        user=user
    )

    initial_status = await avatar_repository.get_training_status(session=db, avatar_id=avatar.id)
    assert initial_status == "available"

    await avatar_repository.set_training_status(session=db, avatar_id=avatar.id, status="training")

    new_status = await avatar_repository.get_training_status(session=db, avatar_id=avatar.id)
    assert new_status == "training"


@pytest.mark.asyncio
async def test_set_training_status_nonexistent_avatar(db: AsyncSession):
    result = await avatar_repository.set_training_status(
        session=db,
        avatar_id=uuid4(),
        status="nonexistent"
    )
    assert result is None


@pytest.mark.asyncio
async def test_get_training_status_nonexistent_avatar(db: AsyncSession):
    result = await avatar_repository.get_training_status(
        session=db,
        avatar_id=uuid4(),
    )
    assert result is None
