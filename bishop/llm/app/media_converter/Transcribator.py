import os
import uuid
from pathlib import Path

import whisper
from moviepy import VideoFileClip


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

    def transcribe_audio(self, file_path: Path) -> str:
        result = self.model.transcribe(str(file_path))
        return result["text"]

    def transcribe_video(self, file_path: Path) -> str:
        with VideoFileClipWithContext(str(file_path)) as video:
            with AudioFileClipWithContext(video) as audio:
                tmp_audio_file_name = f"tmp_audio_{uuid.uuid4()}.mp3"
                audio.write_audiofile(tmp_audio_file_name, verbose=False, logger=None)
                try:
                    text = self.transcribe_audio(Path(tmp_audio_file_name))
                finally:
                    os.remove(tmp_audio_file_name)
        return text


transcribator = Transcribator()
