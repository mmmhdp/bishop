from fastapi import APIRouter, File, UploadFile, Form, HTTPException
import json
from typing import Any
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
    item_in: str = Form(...),
    file: UploadFile = File(...)
) -> Any:
    """
    Upload a new file (audio/video/text) for training and store it in MinIO.
    """
    try:
        item_data = json.loads(item_in)
        item_data["avatar_id"] = avatar_id
        item = TrainMaterialCreate(**item_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")

    try:
        file_url = await train_material_repository.upload_to_minio(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    train_data = TrainMaterial(
        avatar_id=avatar_id,
        type=item.type,  # Expecting this to be passed explicitly now
        url=file_url,
        is_trained_on=False,
    )

    session.add(train_data)
    await session.commit()
    await session.refresh(train_data)
    return train_data
