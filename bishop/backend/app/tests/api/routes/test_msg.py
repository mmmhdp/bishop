import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.chat_message import create_random_chat_message


def test_create_chat_message(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"message": "FooBuzz"}
    response = client.post(
        f"{settings.API_V1_STR}/msgs/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == data["message"]
    assert "id" in content
    assert "owner_id" in content


def test_read_chat_message(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    chat_message = create_random_chat_message(db)
    response = client.get(
        f"{settings.API_V1_STR}/msgs/{chat_message.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == chat_message.message
    assert content["id"] == str(chat_message.id)
    assert content["owner_id"] == str(chat_message.owner_id)


def test_read_chat_message_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/msgs/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "ChatMessage not found"


def test_read_chat_message_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    chat_message = create_random_chat_message(db)
    response = client.get(
        f"{settings.API_V1_STR}/msgs/{chat_message.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_read_chat_messages(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_chat_message(db)
    create_random_chat_message(db)
    response = client.get(
        f"{settings.API_V1_STR}/msgs/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


def test_update_chat_message(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    chat_message = create_random_chat_message(db)
    data = {"message": "Updated message"}
    response = client.put(
        f"{settings.API_V1_STR}/msgs/{chat_message.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == data["message"]
    assert content["id"] == str(chat_message.id)
    assert content["owner_id"] == str(chat_message.owner_id)


def test_update_chat_message_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"message": "Updated message"}
    response = client.put(
        f"{settings.API_V1_STR}/msgs/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "ChatMessage not found"


def test_update_chat_message_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    chat_message = create_random_chat_message(db)
    data = {"message": "Updated message"}
    response = client.put(
        f"{settings.API_V1_STR}/msgs/{chat_message.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_delete_chat_message(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    chat_message = create_random_chat_message(db)
    response = client.delete(
        f"{settings.API_V1_STR}/msgs/{chat_message.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "ChatMessage deleted successfully"


def test_delete_chat_message_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/msgs/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "ChatMessage not found"


def test_delete_chat_message_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    chat_message = create_random_chat_message(db)
    response = client.delete(
        f"{settings.API_V1_STR}/msgs/{chat_message.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"
