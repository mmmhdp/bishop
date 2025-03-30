from fastapi.testclient import TestClient
from sqlmodel.ext.asyncio.session import AsyncSession
import pytest
from uuid import uuid4
from app.common.config import settings
from app.tests.utils.avatar import create_random_avatar
from app.tests.utils.user import create_random_user


def test_create_avatar(
    client: TestClient,
    superuser_token_headers: dict[str, str],
):
    data = {"name": "Cowboy Bebop"}
    response = client.post(
        f"{settings.API_V1_STR}/avatars/", headers=superuser_token_headers, json=data
    )
    assert response.status_code == 200
    assert "id" in response.json()


@pytest.mark.asyncio
async def test_update_avatar(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: AsyncSession,
):
    avatar = await create_random_avatar(db)
    data = {"name": "New Avatar Name"}
    response = client.put(
        f"{settings.API_V1_STR}/avatars/{avatar.id}", headers=superuser_token_headers, json=data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]


@pytest.mark.asyncio
async def test_delete_avatar(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: AsyncSession,
):
    avatar = await create_random_avatar(db)
    response = client.delete(
        f"{settings.API_V1_STR}/avatars/{avatar.id}", headers=superuser_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Avatar deleted successfully"


@pytest.mark.asyncio
async def test_read_user_avatars(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: AsyncSession,
):
    await create_random_avatar(db)
    response = client.get(
        f"{settings.API_V1_STR}/avatars/", headers=superuser_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert "data" in content
    assert isinstance(content["data"], list)


@pytest.mark.asyncio
async def test_start_training_avatar(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: AsyncSession,
):
    avatar = await create_random_avatar(db)
    response = client.post(
        f"{settings.API_V1_STR}/avatars/{avatar.id}/train/start", headers=superuser_token_headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == f"Training started for avatar {
        avatar.id}"


@pytest.mark.asyncio
async def test_stop_training_avatar(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: AsyncSession,
):
    avatar = await create_random_avatar(db)
    response = client.post(
        f"{settings.API_V1_STR}/avatars/{avatar.id}/train/stop", headers=superuser_token_headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == f"Training stop requested for avatar {
        avatar.id}"


@pytest.mark.asyncio
async def test_avatar_not_found(
    client: TestClient,
    superuser_token_headers: dict[str, str],
):
    random_uuid = uuid4()
    response = client.put(
        f"{settings.API_V1_STR}/avatars/{random_uuid}",
        headers=superuser_token_headers,
        json={"name": "Non-existent"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_avatar_permission_denied(
    client: TestClient,
    db: AsyncSession,
):
    password = "password123"
    user = await create_random_user(db, password)
    avatar = await create_random_avatar(db)

    login_data = {"username": user.email, "password": password}
    login_response = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert login_response.status_code == 200
    token_info = login_response.json()

    token_headers = {"Authorization": f"{
        token_info['token_type']} {token_info['access_token']}"}

    response = client.delete(
        f"{settings.API_V1_STR}/avatars/{avatar.id}", headers=token_headers
    )
    assert response.status_code in [400, 403]
