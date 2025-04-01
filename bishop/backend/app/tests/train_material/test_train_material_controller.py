import io
import json
import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession
from minio import Minio

from app.common.config import settings
from app.tests.utils.chat import create_random_chat
from app.tests.utils.utils import get_object_key_from_url


@pytest.mark.asyncio
async def test_upload_file_real_minio(
    async_client: AsyncClient,
    superuser_token_headers: dict,
    db: AsyncSession,
    s3_client: Minio
):
    chat = await create_random_chat(db)
    avatar_id = str(chat.avatar_id)

    item_data = {
        "title": "test ping pong",
        "url": "",
    }

    file_content = b"mock file content"
    files = {
        "file": (
            "mock_train_material.txt", io.BytesIO(file_content), "text/plain"
        )
    }

    data = {
        "item_in": json.dumps(item_data)
    }

    response = await async_client.post(
        f"{settings.API_V1_STR}/avatars/{avatar_id}/train/",
        headers=superuser_token_headers,
        data=data,
        files=files
    )
    print(response.json())
    print(response.url)
    assert response.status_code == 200
    body = response.json()

    assert body["avatar_id"] == avatar_id
    assert body["url"].startswith("http")
    assert body["is_trained_on"] is False

    url = body["url"]
    object_key = get_object_key_from_url(url, settings.MINIO_BUCKET)

    s3_client.remove_object(settings.MINIO_BUCKET, object_key)
