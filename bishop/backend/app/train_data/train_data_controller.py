import logging
import uuid
from typing import Any
import os
from datetime import datetime

from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from sqlmodel import func, select

from app.common.api_deps import CurrentUser, SessionDep
from app.train_data.TrainData import TrainDataCreate, TrainData
from app.train_data.utils import save_in_filesystem
import json
# from app.media_converter import transcribator

router = APIRouter()

@router.post("/")
async def upload_file(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    item_in: str = Form(...),
    file: UploadFile = File(...)
) -> Any:
    """
    Upload new file (audio/video) for training.
    """
    try:
        item_in = TrainDataCreate(**json.loads(item_in))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")

    try:
        path, source_type = await save_in_filesystem(file=file)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=e)
    
    train_data = TrainData(
        avatar_id=item_in.avatar_id,
        type=source_type,
        url=path,
        is_trained_on=False
    )
    session.add(train_data)
    await session.commit()
    await session.refresh(train_data)

    return train_data
