# tests/conftest.py
from minio import Minio
import pytest
import pytest_asyncio
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import delete

from redis import asyncio as AsyncRedis

from app.common.db import async_engine, init_db
from app.user.User import User
from app.main import app
from app.common.config import settings
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers_async


@pytest_asyncio.fixture(scope="session")
async def db() -> AsyncSession:
    async with AsyncSession(async_engine, expire_on_commit=False) as async_session:
        await init_db(async_session)
        yield async_session
        statement = delete(User).where(User.email != settings.FIRST_SUPERUSER)
        await async_session.exec(statement)
        await async_session.commit()
        await init_db(async_session)


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest_asyncio.fixture
async def cache_client() -> AsyncRedis:
    client = AsyncRedis.from_url(
        url=settings.REDIS_URL,
        decode_responses=True
    )
    yield client
    await client.close()


@pytest.fixture
def s3_client() -> Minio:
    client = Minio(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_USE_SSL,
    )

    if not client.bucket_exists(settings.MINIO_BUCKET):
        client.make_bucket(settings.MINIO_BUCKET)

    return client


@pytest_asyncio.fixture
async def superuser_token_headers(async_client: AsyncClient) -> dict[str, str]:
    return await get_superuser_token_headers_async(async_client)


@pytest_asyncio.fixture(scope="function")
async def normal_user_token_headers(
    async_client: AsyncClient, db: AsyncSession
) -> dict[str, str]:
    return await authentication_token_from_email(
        client=async_client, email=settings.EMAIL_TEST_USER, db=db
    )
