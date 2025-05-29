import uuid
import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession
from unittest.mock import AsyncMock, patch

from app.common.config import settings
from app.common.logging_service import logger
from app.avatar.Avatar import Avatar
from app.avatar.avatar_controller import AVATAR_STATUS
from app.tests.utils.avatar import create_random_avatar
from app.tests.utils.user import create_random_user


@pytest.mark.asyncio
async def test_create_avatar(
    async_client: AsyncClient,
    superuser_token_headers: dict[str, str],
):
    data = {"name": "Cowboy Bebop"}
    response = await async_client.post(
        f"{settings.API_V1_STR}/avatars/",
        headers=superuser_token_headers,
        json=data
    )
    assert response.status_code == 200
    content = response.json()
    assert "id" in content
    assert content["name"] == "Cowboy Bebop"
    assert content["status"] == AVATAR_STATUS["available"]


@pytest.mark.asyncio
async def test_update_avatar(
    async_client: AsyncClient,
    superuser_token_headers: dict[str, str],
    db: AsyncSession,
):
    avatar = await create_random_avatar(db)
    data = {"name": "Updated Avatar"}
    response = await async_client.put(
        f"{settings.API_V1_STR}/avatars/{avatar.id}",
        headers=superuser_token_headers,
        json=data
    )
    assert response.status_code == 200
    assert response.json()["name"] == data["name"]


@pytest.mark.asyncio
async def test_delete_avatar(
    async_client: AsyncClient,
    superuser_token_headers: dict[str, str],
    db: AsyncSession,
):
    avatar = await create_random_avatar(db)
    response = await async_client.delete(
        f"{settings.API_V1_STR}/avatars/{avatar.id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Avatar deleted successfully"


@pytest.mark.asyncio
async def test_read_user_avatars(
    async_client: AsyncClient,
    superuser_token_headers: dict[str, str],
    db: AsyncSession,
):
    await create_random_avatar(db)
    response = await async_client.get(
        f"{settings.API_V1_STR}/avatars/",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert "data" in content
    assert isinstance(content["data"], list)
    assert len(content["data"]) >= 1


@pytest.mark.asyncio
async def test_read_avatar_success(
    async_client: AsyncClient,
    superuser_token_headers: dict[str, str],
    db: AsyncSession,
):
    avatar = await create_random_avatar(db)
    response = await async_client.get(
        f"{settings.API_V1_STR}/avatars/{avatar.id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(avatar.id)
    assert data["name"] == avatar.name


@pytest.mark.asyncio
async def test_read_avatar_not_found(
    async_client: AsyncClient,
    superuser_token_headers: dict[str, str],
):
    random_uuid = uuid.uuid4()
    response = await async_client.get(
        f"{settings.API_V1_STR}/avatars/{random_uuid}",
        headers=superuser_token_headers
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Avatar not found"


@pytest.mark.asyncio
async def test_read_avatar_not_enough_permissions(
    async_client: AsyncClient,
    db: AsyncSession,
):
    avatar = await create_random_avatar(db)
    password = "userpass123"
    user = await create_random_user(db, password=password)

    login_response = await async_client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": user.email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token_info = login_response.json()
    headers = {
        "Authorization": f"{token_info['token_type']} {token_info['access_token']}"
    }

    response = await async_client.get(
        f"{settings.API_V1_STR}/avatars/{avatar.id}",
        headers=headers
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Not enough permissions"


@pytest.mark.asyncio
@patch("app.avatar.avatar_broker_service.send_train_start_message", new_callable=AsyncMock)
async def test_start_training_avatar(
    mock_send_train_start_message: AsyncMock,
    async_client: AsyncClient,
    superuser_token_headers: dict[str, str],
    db: AsyncSession,
):
    avatar = await create_random_avatar(db)

    logger.info(f"BEFORE Avatar {avatar.id} status: {avatar.status}")
    response = await async_client.post(
        f"{settings.API_V1_STR}/avatars/{avatar.id}/train/start",
        headers=superuser_token_headers,
    )
    logger.info(f"AFTER Avatar {avatar.id} status: {avatar.status}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Training started for avatar {
        avatar.id}"
    mock_send_train_start_message.assert_called_once()

    refreshed = await db.get(Avatar, avatar.id)
    await db.refresh(refreshed)
    logger.info(f"Avatar {refreshed.id} status: {refreshed.status}")
    assert refreshed.status == AVATAR_STATUS["training"]


@pytest.mark.asyncio
@patch("app.avatar.avatar_broker_service.send_train_stop_message", new_callable=AsyncMock)
async def test_stop_training_avatar(
    mock_send_train_stop_message: AsyncMock,
    async_client: AsyncClient,
    superuser_token_headers: dict[str, str],
    db: AsyncSession,
):
    avatar = await create_random_avatar(db)
    avatar.status = AVATAR_STATUS["training"]
    db.add(avatar)
    await db.commit()

    response = await async_client.post(
        f"{settings.API_V1_STR}/avatars/{avatar.id}/train/stop",
        headers=superuser_token_headers
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Training stop requested for avatar {
        avatar.id}"
    mock_send_train_stop_message.assert_called_once()

    refreshed = await db.get(Avatar, avatar.id)
    await db.refresh(refreshed)
    assert refreshed.status == AVATAR_STATUS["available"]


@pytest.mark.asyncio
async def test_get_training_status(
    async_client: AsyncClient,
    superuser_token_headers: dict[str, str],
    db: AsyncSession,
):
    avatar = await create_random_avatar(db)
    avatar.status = AVATAR_STATUS["training"]
    db.add(avatar)
    await db.commit()

    response = await async_client.post(
        f"{settings.API_V1_STR}/avatars/{avatar.id}/train/status",
        headers=superuser_token_headers
    )

    assert response.status_code == 200
    assert response.json()["message"] == AVATAR_STATUS["training"]


@pytest.mark.asyncio
async def test_get_training_status_not_found(
    async_client: AsyncClient,
    superuser_token_headers: dict[str, str],
):
    random_uuid = uuid.uuid4()
    response = await async_client.post(
        f"{settings.API_V1_STR}/avatars/{random_uuid}/train/status",
        headers=superuser_token_headers
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Avatar not found"


@pytest.mark.asyncio
async def test_avatar_not_found(
    async_client: AsyncClient,
    superuser_token_headers: dict[str, str],
):
    random_uuid = uuid.uuid4()
    response = await async_client.put(
        f"{settings.API_V1_STR}/avatars/{random_uuid}",
        headers=superuser_token_headers,
        json={"name": "Non-existent Avatar"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Avatar not found"


@pytest.mark.asyncio
async def test_avatar_permission_denied(
    async_client: AsyncClient,
    db: AsyncSession,
):
    password = "password123"
    user = await create_random_user(db, password=password)
    avatar = await create_random_avatar(db)

    login_response = await async_client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": user.email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token_info = login_response.json()
    token_headers = {
        "Authorization": f"{token_info['token_type']} {token_info['access_token']}"
    }

    response = await async_client.delete(
        f"{settings.API_V1_STR}/avatars/{avatar.id}",
        headers=token_headers
    )
    assert response.status_code in [400, 403]

