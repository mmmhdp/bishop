import io
import uuid
import pytest
from minio import Minio

from app.train_material import train_material_repository
from app.common.config import settings
from starlette.datastructures import UploadFile


@pytest.fixture
def dummy_upload_file():
    file = UploadFile(
        filename="sample.mp3",
        file=io.BytesIO(b"fake audio content")
    )
    return file


@pytest.mark.asyncio
async def test_upload_to_s3_success(s3_client: Minio, dummy_upload_file):
    user_id = uuid.uuid4()
    avatar_id = uuid.uuid4()

    url = await train_material_repository.upload_to_s3(
        file=dummy_upload_file,
        user_id=user_id,
        avatar_id=avatar_id
    )

    assert url.startswith(settings.MINIO_URL)
    assert settings.MINIO_BUCKET in url

    object_key = url.split(f"{settings.MINIO_BUCKET}/")[1]

    stat = s3_client.stat_object(settings.MINIO_BUCKET, object_key)
    assert stat.size == len(b"fake audio content")

    s3_client.remove_object(settings.MINIO_BUCKET, object_key)
