import uuid
import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.config import settings
from app.tests.utils.chat import create_random_chat
from app.tests.utils.chat_message import create_random_chat_message
from app.tests.utils.chat import random_lower_string


@pytest.mark.asyncio
async def test_create_message(async_client: AsyncClient, superuser_token_headers: dict, db: AsyncSession):
    chat = await create_random_chat(db)
    avatar_id = str(chat.avatar_id)
    chat_id = str(chat.id)
    data = {
        "title": random_lower_string(),
        "text": "Ping"
    }
    response = await async_client.post(
        f"{settings.API_V1_STR}/avatars/{avatar_id}/chat/{chat_id}/msgs/",
        headers=superuser_token_headers,
        json=data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["text"] == data["text"]
    assert "id" in content


@pytest.mark.asyncio
async def test_read_messages(async_client: AsyncClient, superuser_token_headers: dict, db: AsyncSession):
    msg = await create_random_chat_message(db)
    avatar_id = str(msg.avatar_id)
    chat_id = str(msg.chat_id)

    response = await async_client.get(
        f"{settings.API_V1_STR}/avatars/{avatar_id}/chat/{chat_id}/msgs/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content["data"], list)
    assert any(m["id"] == str(msg.id) for m in content["data"])


@pytest.mark.asyncio
async def test_read_message(async_client: AsyncClient, superuser_token_headers: dict, db: AsyncSession):
    msg = await create_random_chat_message(db)
    avatar_id = str(msg.avatar_id)
    chat_id = str(msg.chat_id)

    response = await async_client.get(
        f"{settings.API_V1_STR}/avatars/{avatar_id}/chat/{chat_id}/msgs/{msg.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(msg.id)
    assert content["text"] == msg.text


@pytest.mark.asyncio
async def test_update_message(async_client: AsyncClient, superuser_token_headers: dict, db: AsyncSession):
    msg = await create_random_chat_message(db)
    avatar_id = str(msg.avatar_id)
    chat_id = str(msg.chat_id)

    new_text = "Updated content"
    response = await async_client.put(
        f"{settings.API_V1_STR}/avatars/{avatar_id}/chat/{chat_id}/msgs/{msg.id}",
        headers=superuser_token_headers,
        json={"text": new_text}
    )
    assert response.status_code == 200
    content = response.json()
    assert content["text"] == new_text


@pytest.mark.asyncio
async def test_delete_message(async_client: AsyncClient, superuser_token_headers: dict, db: AsyncSession):
    msg = await create_random_chat_message(db)
    avatar_id = str(msg.avatar_id)
    chat_id = str(msg.chat_id)

    response = await async_client.delete(
        f"{settings.API_V1_STR}/avatars/{avatar_id}/chat/{chat_id}/msgs/{msg.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Message deleted successfully"


@pytest.mark.asyncio
async def test_get_response_for_message_not_found(async_client: AsyncClient, superuser_token_headers: dict, db: AsyncSession):
    chat = await create_random_chat(db)
    avatar_id = str(chat.avatar_id)
    chat_id = str(chat.id)
    random_message_id = uuid.uuid4()

    response = await async_client.get(
        f"{settings.API_V1_STR}/avatars/{avatar_id}/chat/{
            chat_id}/msgs/{random_message_id}/response/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
