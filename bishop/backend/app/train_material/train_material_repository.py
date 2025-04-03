import uuid
from io import BytesIO
from fastapi import UploadFile, HTTPException
from app.common.config import settings
from app.common.db import minio_client
from minio.error import S3Error
from starlette.concurrency import run_in_threadpool

# Allowed extensions grouped by type
# ALLOWED_EXTENSIONS = {
#    "audio": {"mp3", "wav", "m4a", "aac", "flac"},
#    "video": {"mp4", "avi", "mov", "mkv", "webm"},
#    "text": {"txt", "csv", "json"}
# }

ALLOWED_EXTENSIONS = {
    "audio": {"mp3", "m4a", "ogg"},
    "video": {"mp4"},
    "text": {"txt", "csv", "json"}
}


def detect_file_type(file_ext: str) -> str:
    """
    Detects the high-level file type from extension.
    Raises if unsupported.
    """
    for type_group, ext_list in ALLOWED_EXTENSIONS.items():
        if file_ext.lower() in ext_list:
            return type_group
    raise HTTPException(
        status_code=400, detail=f"Unsupported file extension: .{file_ext}")


async def upload_to_s3(file: UploadFile, user_id: uuid.UUID, avatar_id: uuid.UUID) -> str:
    """
    Uploads file to MinIO with organized path and returns the full URL.
    Path format: users/{user_id}/avatars/{avatar_id}/{type}/{file_id}.{ext}
    """
    file_ext = file.filename.split('.')[-1]
    file_type = detect_file_type(file_ext)
    file_id = uuid.uuid4()
    object_name = f"users/{user_id}/avatars/{
        avatar_id}/{file_type}/{file_id}.{file_ext}"

    try:
        file_data = await file.read()
        file_size = len(file_data)

        kwargs = dict(
            bucket_name=settings.MINIO_BUCKET,
            object_name=object_name,
            data=BytesIO(file_data),
            length=file_size,
            content_type=file.content_type,
        )
        await run_in_threadpool(minio_client.put_object, **kwargs)
    except S3Error as exc:
        raise RuntimeError(f"Failed to upload to MinIO: {exc}")

    return f"{settings.MINIO_URL}/{settings.MINIO_BUCKET}/{object_name}"
