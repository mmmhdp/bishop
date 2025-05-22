from fastapi import APIRouter, File, UploadFile, HTTPException, Form
import uuid

from app.common.logging_service import logger
from app.common.api_deps import SessionDep, CurrentUser
from app.train_material.TrainMaterial import TrainMaterialCreate, TrainMaterial
from app.train_material import train_material_repository

router = APIRouter()


@router.post("/")
async def upload_file(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    avatar_id: uuid.UUID,
    type: str = Form(...),
    file: UploadFile = File(...)
) -> TrainMaterial:
    """
    Upload a new file for training and store it in S3 storage.
    """

    logger.info(f"Uploading file for avatar {
                avatar_id} by user {current_user.id}")

    try:
        file_url = await train_material_repository.upload_to_s3(
            user_id=current_user.id,
            avatar_id=avatar_id,
            file=file, type=type,
            session=session
        )
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    train_data = await train_material_repository.create_train_material(
        session=session,
        avatar_id=avatar_id,
        file_url=file_url,
        type=type
    )

    return train_data
