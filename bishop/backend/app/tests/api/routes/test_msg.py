import uuid

from fastapi.testclient import TestClient
from sqlmodel.ext.asyncio.session import AsyncSession
import pytest
import pytest_asyncio

from app.common.config import settings
from app.tests.utils.chat_message import create_random_chat_message
from app.tests.utils.chat import create_random_chat

@pytest.mark.asyncio
async def test_create_chat_message(
    client: TestClient, superuser_token_headers: dict[str, str], db: AsyncSession
) -> None:
    chat = await create_random_chat(db=db)
    id_for_json = str(chat.id)
    data = {"text": "FooBuzz", "chat_id": id_for_json}
    response = client.post(
        f"{settings.API_V1_STR}/msgs/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["text"] == data["text"]
    assert "id" in content

# TODO: get wihtout id not ready
# @pytest.mark.asyncio
# async def test_read_chat_message(
#     client: TestClient, superuser_token_headers: dict[str, str], db: AsyncSession
# ) -> None:
#     chat_message = await create_random_chat_message(db)
#     response = client.get(
#         f"{settings.API_V1_STR}/msgs/{chat_message.id}",
#         headers=superuser_token_headers,
#     )
#     assert response.status_code == 200
#     content = response.json()
#     assert content["text"] == chat_message.text
#     assert content["id"] == str(chat_message.id)
#     assert content["owner_id"] == str(chat_message.owner_id)


def test_read_chat_message_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/msgs/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Message not found"


# TODO: not enough perm not ready
# @pytest.mark.asyncio
# async def test_read_chat_message_not_enough_permissions(
#     client: TestClient, normal_user_token_headers: dict[str, str], db: AsyncSession
# ) -> None:
#     chat_message = await create_random_chat_message(db)
#     response = client.get(
#         f"{settings.API_V1_STR}/msgs/{chat_message.id}",
#         headers=normal_user_token_headers,
#     )
#     assert response.status_code == 400
#     content = response.json()
#     assert content["detail"] == "Not enough permissions"

# TODO: get wihtout id not ready
# @pytest.mark.asyncio
# async def test_read_chat_messages(
#     client: TestClient, superuser_token_headers: dict[str, str], db: AsyncSession
# ) -> None:
#     await create_random_chat_message(db)
#     await create_random_chat_message(db)
#     response = client.get(
#         f"{settings.API_V1_STR}/msgs/",
#         headers=superuser_token_headers,
#     )
#     assert response.status_code == 200
#     content = response.json()
#     assert len(content["data"]) >= 2


@pytest.mark.asyncio
async def test_update_chat_message(
    client: TestClient, superuser_token_headers: dict[str, str], db: AsyncSession
) -> None:
    chat_message = await create_random_chat_message(db)
    data = {"text": "Updated text"}
    response = client.put(
        f"{settings.API_V1_STR}/msgs/{chat_message.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["text"] == data["text"]
    assert content["id"] == str(chat_message.id)


def test_update_chat_message_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"text": "Updated text"}
    response = client.put(
        f"{settings.API_V1_STR}/msgs/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Message not found"

# TODO: not en perm not ready
# @pytest.mark.asyncio
# async def test_update_chat_message_not_enough_permissions(
#     client: TestClient, normal_user_token_headers: dict[str, str], db: AsyncSession
# ) -> None:
#     chat_message = await create_random_chat_message(db)
#     data = {"text": "Updated text"}
#     response = client.put(
#         f"{settings.API_V1_STR}/msgs/{chat_message.id}",
#         headers=normal_user_token_headers,
#         json=data,
#     )
#     assert response.status_code == 400
#     content = response.json()
#     assert content["detail"] == "Not enough permissions"


@pytest.mark.asyncio
async def test_delete_chat_message(
    client: TestClient, superuser_token_headers: dict[str, str], db: AsyncSession
) -> None:
    chat_message = await create_random_chat_message(db)
    response = client.delete(
        f"{settings.API_V1_STR}/msgs/{chat_message.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Message deleted successfully"


def test_delete_chat_message_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/msgs/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Message not found"

# TODO: not en perm not ready
# @pytest.mark.asyncio
# async def test_delete_chat_message_not_enough_permissions(
#     client: TestClient, normal_user_token_headers: dict[str, str], db: AsyncSession
# ) -> None:
#     chat_message = await create_random_chat_message(db)
#     response = client.delete(
#         f"{settings.API_V1_STR}/msgs/{chat_message.id}",
#         headers=normal_user_token_headers,
#     )
#     assert response.status_code == 400
#     content = response.json()
#     assert content["detail"] == "Not enough permissions"
