import whisper
from moviepy import VideoFileClip
import uuid
import os
from app.user.User import User
from app.transcription.Transcription import Transcription, SourceType
from sqlmodel.ext.asyncio.session import AsyncSession
from app.transcription import transcription_repository

class VideoFileClipWithContext:
    def __init__(self, video_path):
        self.video_path = video_path
        self.video_clip = None

    def __enter__(self):
        self.video_clip = VideoFileClip(self.video_path)
        return self.video_clip

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.video_clip:
            self.video_clip.close()


class AudioFileClipWithContext:
    def __init__(self, video):
        self.video = video
        self.audio_clip = None

    def __enter__(self):
        self.audio_clip = self.video.audio
        return self.audio_clip

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.audio_clip:
            self.audio_clip.close()


class Transcribator:
    def __init__(self, model_type: str = "base"):
        self.model_type = model_type
        self.model = whisper.load_model(self.model_type)

    # def transcribe_video(self, file_path: str):
    #     with VideoFileClipWithContext("test_video.mp4") as video:
    #         with AudioFileClipWithContext(video) as audio:
    #                 tmp_audio_file_name = "tmp_audio_" + str(uuid.uuid4()) + ".mp3"
    #                 audio.write_audiofile(tmp_audio_file_name)
    #                 transcription_uuid = self.transcribe_audio_impl(tmp_audio_file_name)
    #                 os.remove(tmp_audio_file_name)
    #     return transcription_uuid
    
    async def transcribe_audio_and_save_in_db(self, file_path: str, cur_user: User, session: AsyncSession) -> Transcription:
        result = self.transcribe_audio_impl(file_path)
        transcription = await transcription_repository.create_transcription(
            session=session,
            text=result,
            original_source=SourceType.AUDIO,
            owner_id=cur_user.id,
            owner=cur_user
            )
        return transcription

    
    def transcribe_audio_impl(self, file_path: str) -> str:
        result = self.model.transcribe(file_path)
        return result["text"]
    
transcribator = Transcribator()
