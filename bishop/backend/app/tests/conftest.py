from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlmodel import delete
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.db import async_engine, init_db
from app.main import app
from app.models import Item, User
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers


@pytest_asyncio.fixture(scope="session")
async def db():
    async with AsyncSession(async_engine) as async_session:
        await init_db(async_session)
        yield async_session
        statement = delete(Item)
        await async_session.exec(statement)
        statement = delete(User)
        await async_session.exec(statement)
        await async_session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest_asyncio.fixture(scope="module")
async def normal_user_token_headers(client: TestClient, db: AsyncSession) -> dict[str, str]:
    tokens = await authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )
    return tokens
