import io
import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession
from minio import Minio

from app.common.config import settings
from app.tests.utils.avatar import create_random_avatar
from app.broker.broker_utils import get_object_key_from_url


@pytest.mark.asyncio
async def test_upload_file_real_minio(
    async_client: AsyncClient,
    superuser_token_headers: dict,
    db: AsyncSession,
    s3_client: Minio
):
    avatar = await create_random_avatar(db)
    avatar_id = str(avatar.id)

    data = {
        "type": "text"
    }

    files = {
        "file": (
            "mock_train_material.txt",
            io.BytesIO(b"mock file content"),
            "text/plain"
        )
    }

    response = await async_client.post(
        f"{settings.API_V1_STR}/avatars/{avatar_id}/train/",
        headers=superuser_token_headers,
        data=data,
        files=files
    )

    assert response.status_code == 200
    body = response.json()

    assert body["avatar_id"] == avatar_id
    assert body["url"].startswith("http")
    assert body["is_trained_on"] is False
    assert body["type"] == "text"

    object_key = get_object_key_from_url(body["url"], settings.MINIO_BUCKET)
    s3_client.remove_object(settings.MINIO_BUCKET, object_key)
