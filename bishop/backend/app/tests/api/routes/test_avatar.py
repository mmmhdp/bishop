import uuid

from fastapi.testclient import TestClient
from sqlmodel.ext.asyncio.session import AsyncSession
import pytest
import pytest_asyncio

from app.common.config import settings
from app.tests.utils.chat_message import create_random_chat_message
from app.tests.utils.chat import create_random_chat
from app.tests.utils.avatar import create_random_avatar
from app.tests.utils.user import create_random_user


def test_create_avatar(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"name": "Cowboy Bebop"}
    response = client.post(
        f"{settings.API_V1_STR}/avatar/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    assert "avatar_id" in response.json()


@pytest.mark.asyncio
async def test_update_avatar(
    client: TestClient, superuser_token_headers: dict[str, str], db: AsyncSession
) -> None:
    avatar = await create_random_avatar(db)
    data = {"name": "Cowboy Bebop"}
    response = client.put(
        f"{settings.API_V1_STR}/avatar/{avatar.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]


@pytest.mark.asyncio
async def test_delete_avatar(
    client: TestClient, superuser_token_headers: dict[str, str], db: AsyncSession
) -> None:
    avatar = await create_random_avatar(db)
    response = client.delete(
        f"{settings.API_V1_STR}/avatar/{avatar.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Avatar deleted successfully"

# TODO: more cases with normal users + failure cases