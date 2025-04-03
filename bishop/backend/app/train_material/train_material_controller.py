from fastapi import APIRouter, File, UploadFile, HTTPException, Form
import json
import uuid

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
    try:
        file_url = await train_material_repository.upload_to_s3(
            user_id=current_user.id, avatar_id=avatar_id, file=file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    train_data = TrainMaterial(
        avatar_id=avatar_id,
        url=file_url,
        type=type,
        is_trained_on=False,
    )

    session.add(train_data)
    await session.commit()
    await session.refresh(train_data)
    return train_data
