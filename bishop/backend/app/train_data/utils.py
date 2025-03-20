from fastapi import UploadFile
import os
from datetime import datetime
from app.train_data.TrainData import SourceType

UPLOAD_DIR = "uploads"
UPLOAD_AUDIO_DIR = UPLOAD_DIR + "/audio"
UPLOAD_VIDEO_DIR = UPLOAD_DIR + "/video"

os.makedirs(UPLOAD_AUDIO_DIR, exist_ok=True)
os.makedirs(UPLOAD_VIDEO_DIR, exist_ok=True)

ALLOWED_VIDEO_FORMATS = ["mp4"]
ALLOWED_AUDIO_FORMATS = ["mp3", "m4a", "ogg"]

async def save_in_filesystem(file: UploadFile) -> tuple[str, SourceType]:
    file_format = file.filename.rsplit(".", maxsplit=1)[-1] # audio.mp3 -> mp3
    if file_format == file.filename:
        raise ValueError("Wrong file format")
    
    file_format = file_format.lower()

    if file_format in ALLOWED_AUDIO_FORMATS:
        source_type = SourceType.AUDIO
        savedir = UPLOAD_AUDIO_DIR
    elif file_format in ALLOWED_VIDEO_FORMATS:
        source_type = SourceType.VIDEO
        savedir = UPLOAD_VIDEO_DIR
    else:
        raise ValueError("Wrong file format")
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(savedir, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return file_path, source_type


    