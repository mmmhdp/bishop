import logging
import uuid
from typing import Any
import os
from datetime import datetime

from fastapi import APIRouter, File, UploadFile, HTTPException
from sqlmodel import func, select

from app.common.api_deps import CurrentUser, SessionDep
from app.media_converter import transcribator

router = APIRouter()

UPLOAD_DIR_AUDIO = "uploads/audio"
os.makedirs(UPLOAD_DIR_AUDIO, exist_ok=True)


@router.post("/audio/") # TODO: response_model=some_model?
async def upload_audio(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(...)
) -> Any:
    """
    Transcribe new audiofile.
    """

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR_AUDIO, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    transcription = await transcribator.transcribe_audio_and_save_in_db(file_path, current_user, session)
    
    return {"transcription": transcription.text, "uuid": transcription.id}
