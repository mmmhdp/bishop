from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession
from app.user import user_repository
from app.user.User import User, UserCreate, UserUpdate
from app.tests.utils.utils import random_email, random_lower_string


async def create_random_user(db: AsyncSession, password: str = None) -> User:
    if not password:
        password = random_lower_string()
    email = random_email()
    user_in = UserCreate(email=email, password=password)
    return await user_repository.create_user(session=db, user_create=user_in)


async def user_authentication_headers(
    *, client: AsyncClient, email: str, password: str
) -> dict[str, str]:
    data = {"username": email, "password": password}
    r = await client.post(
        "/api/v1/login/access-token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response = r.json()
    return {"Authorization": f"Bearer {response['access_token']}"}


async def authentication_token_from_email(
    *, client: AsyncClient, email: str, db: AsyncSession
) -> dict[str, str]:
    password = random_lower_string()
    user = await user_repository.get_user_by_email(session=db, email=email)
    if not user:
        user = await user_repository.create_user(
            session=db, user_create=UserCreate(email=email, password=password)
        )
    else:
        user = await user_repository.update_user(
            session=db,
            db_user=user,
            user_in=UserUpdate(password=password)
        )
    return await user_authentication_headers(client=client, email=email, password=password)

