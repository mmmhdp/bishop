from typing import Any

from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.security.security_service import get_password_hash, verify_password


from app.user.User import (
    User, UserCreate, UserUpdate, UsersPublic
)


async def get_users(*, session: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    count_statement = select(func.count()).select_from(User)
    count_result = await session.exec(count_statement)
    count = count_result.one()

    statement = select(User).offset(skip).limit(limit)
    users_result = await session.exec(statement)
    users = users_result.all()

    return UsersPublic(data=users, count=count)


async def create_user(*, session: AsyncSession, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={
            "hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj


async def update_user(*, session: AsyncSession, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def get_user_by_email(*, session: AsyncSession, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user_result = await session.exec(statement)
    session_user = session_user_result.first()
    return session_user


async def authenticate(*, session: AsyncSession, email: str, password: str) -> User | None:
    db_user = await get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user
