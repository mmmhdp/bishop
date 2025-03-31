import uuid
import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.chat.Chat import ChatCreate, ChatUpdate
from app.tests.utils.avatar import create_random_avatar
from app.tests.utils.utils import random_lower_string


@pytest.mark.asyncio
async def test_create_chat(async_client: AsyncClient, superuser_token_headers: dict[str, str], db: AsyncSession):
    avatar = await create_random_avatar(db)
    data = {"title": random_lower_string()}
    response = await async_client.post(
        f"/api/v1/avatars/{avatar.id}/chat/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    assert "chat_id" in response.json()


@pytest.mark.asyncio
async def test_create_duplicate_chat_fails(async_client: AsyncClient, superuser_token_headers: dict[str, str], db: AsyncSession):
    avatar = await create_random_avatar(db)
    title = random_lower_string()
    data = {"title": title}

    await async_client.post(
        f"/api/v1/avatars/{avatar.id}/chat/",
        headers=superuser_token_headers,
        json=data,
    )
    response = await async_client.post(
        f"/api/v1/avatars/{avatar.id}/chat/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 400
    assert response.json()[
        "detail"] == "The chat with this title already exists for that avatar"


@pytest.mark.asyncio
async def test_get_chats_for_avatar(async_client: AsyncClient, superuser_token_headers: dict[str, str], db: AsyncSession):
    avatar = await create_random_avatar(db)
    await async_client.post(
        f"/api/v1/avatars/{avatar.id}/chat/",
        headers=superuser_token_headers,
        json={"title": random_lower_string()},
    )
    response = await async_client.get(
        f"/api/v1/avatars/{avatar.id}/chat/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_chat_by_id(async_client: AsyncClient, superuser_token_headers: dict[str, str], db: AsyncSession):
    avatar = await create_random_avatar(db)
    title = random_lower_string()
    create_resp = await async_client.post(
        f"/api/v1/avatars/{avatar.id}/chat/",
        headers=superuser_token_headers,
        json={"title": title},
    )
    chat_id = create_resp.json()["chat_id"]
    response = await async_client.get(
        f"/api/v1/avatars/{avatar.id}/chat/{chat_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == title


@pytest.mark.asyncio
async def test_update_chat(async_client: AsyncClient, superuser_token_headers: dict[str, str], db: AsyncSession):
    avatar = await create_random_avatar(db)
    old_title = random_lower_string()
    new_title = random_lower_string()
    create_resp = await async_client.post(
        f"/api/v1/avatars/{avatar.id}/chat/",
        headers=superuser_token_headers,
        json={"title": old_title},
    )
    chat_id = create_resp.json()["chat_id"]
    response = await async_client.put(
        f"/api/v1/avatars/{avatar.id}/chat/{chat_id}",
        headers=superuser_token_headers,
        json={"title": new_title},
    )
    assert response.status_code == 200
    assert response.json()["title"] == new_title


@pytest.mark.asyncio
async def test_delete_chat(async_client: AsyncClient, superuser_token_headers: dict[str, str], db: AsyncSession):
    avatar = await create_random_avatar(db)
    create_resp = await async_client.post(
        f"/api/v1/avatars/{avatar.id}/chat/",
        headers=superuser_token_headers,
        json={"title": random_lower_string()},
    )
    chat_id = create_resp.json()["chat_id"]
    delete_resp = await async_client.delete(
        f"/api/v1/avatars/{avatar.id}/chat/{chat_id}",
        headers=superuser_token_headers,
    )
    assert delete_resp.status_code == 200
    assert delete_resp.json() == {"ok": True}


@pytest.mark.asyncio
async def test_get_chat_not_found(async_client: AsyncClient, superuser_token_headers: dict[str, str]):
    response = await async_client.get(
        f"/api/v1/avatars/{uuid.uuid4()}/chat/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Chat not found"


@pytest.mark.asyncio
async def test_update_chat_not_found(async_client: AsyncClient, superuser_token_headers: dict[str, str]):
    response = await async_client.put(
        f"/api/v1/avatars/{uuid.uuid4()}/chat/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json={"title": "Updated"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Chat not found"


@pytest.mark.asyncio
async def test_delete_chat_not_found(async_client: AsyncClient, superuser_token_headers: dict[str, str]):
    response = await async_client.delete(
        f"/api/v1/avatars/{uuid.uuid4()}/chat/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Chat not found"
