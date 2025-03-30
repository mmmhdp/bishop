from fastapi.testclient import TestClient
from sqlmodel.ext.asyncio.session import AsyncSession
import pytest

from app.common.config import settings
from app.tests.utils.avatar import create_random_avatar


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
