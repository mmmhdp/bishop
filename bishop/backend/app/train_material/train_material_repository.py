import uuid
from fastapi import UploadFile
from app.common.config import settings
from app.common.db import minio_client
from minio.error import S3Error
from io import BytesIO


async def upload_to_minio(file: UploadFile) -> str:
    """
    Uploads file to MinIO and returns the file URL.
    """
    file_ext = file.filename.split('.')[-1]
    object_name = f"{uuid.uuid4()}.{file_ext}"

    try:
        file_data = await file.read()
        file_size = len(file_data)

        minio_client.put_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=object_name,
            data=BytesIO(file_data),
            length=file_size,
            content_type=file.content_type,
        )
    except S3Error as exc:
        raise RuntimeError(f"Failed to upload to MinIO: {exc}")

    return f"{settings.MINIO_URL}/{settings.MINIO_BUCKET}/{object_name}"
