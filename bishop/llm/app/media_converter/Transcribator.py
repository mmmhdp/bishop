from pathlib import Path

import whisper
from moviepy import VideoFileClip

from app.common.config import settings


class Transcribator:
    def __init__(self, model_type: str = "base"):
        self.model_type = model_type
        self.model = whisper.load_model(self.model_type)

    def transcribe_audio(
            self,
            audio_path: Path,
            output_dir: Path = Path(settings.INTERIM_DATA_DIR),
    ) -> Path:
        """
        Transcribes an audio file to text and saves the result as a .txt file.

        Args:
            audio_path (Path): Path to the input audio file
            output_dir (Path): Directory to save the transcription (default: settings.INTERIM_DATA_DIR)

        Returns:
            Path: Path to the output text file
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        result = self.model.transcribe(str(audio_path))
        output_path = output_dir / (audio_path.stem + ".txt")
        with output_path.open('w', encoding='utf-8') as f:
            f.write(result['text'])
        return str(output_path)

    def transcribe_video(
            self,
            video_path: Path,
            output_dir: Path = Path(settings.INTERIM_DATA_DIR),
    ) -> Path:
        """
        Extracts audio from a video file, transcribes it to text, and saves as a .txt file.

        Args:
            video_path (Path): Path to the input video file
            output_dir (Path): Directory to save the transcription (default: settings.INTERIM_DATA_DIR)

        Returns:
            Path: Path to the output text file
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        temp_audio = output_dir / "temp_audio.wav"
        try:
            video = VideoFileClip(str(video_path))
            video.audio.write_audiofile(str(temp_audio), codec='pcm_s16le', logger=None)
            video.close()
            result = self.model.transcribe(str(temp_audio))
            output_path = output_dir / (video_path.stem + ".txt")
            with output_path.open('w', encoding='utf-8') as f:
                f.write(result['text'])
            return str(output_path)
        finally:
            if temp_audio.exists():
                temp_audio.unlink()


transcribator = Transcribator()
