from sqlmodel.ext.asyncio.session import AsyncSession

from app.avatar import avatar_repository
from app.avatar.Avatar import Avatar, AvatarCreate

from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


async def create_random_avatar(db: AsyncSession) -> Avatar:
    user = await create_random_user(db)
    owner_id = user.id
    assert owner_id is not None

    avatar_in = AvatarCreate(name=random_lower_string())
    avatar = await avatar_repository.create_avatar(session=db, avatar_create=avatar_in, user=user)

    return avatar
