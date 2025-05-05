from pathlib import Path
from typing import List

from tqdm import tqdm

from app.common.config import settings
from app.common.logging_service import logger
from app.media_converter import transcribator
from app.s3_storage import s3_storage

# Supported extensions for each type
AUDIO_FORMATS = {"mp3", "m4a", "ogg"}
VIDEO_FORMATS = {"mp4"}
TEXT_FORMATS = {"txt", "csv", "json"}


def download_data(
        s3_urls: List[Path],
        output_dir: Path = settings.RAW_DATA_DIR,
) -> List[Path]:
    """
    Uploading files from S3 to a local directory.

    :param s3_urls: A list of file URLs in S3.
    :param output_dir: The local directory for saving files.
    :return: A list of local paths to downloaded files.
    """
    logger.info("Processing dataset...")
    local_files = []

    for s3_url in tqdm(s3_urls, desc="Downloading files"):
        try:
            local_path = s3_storage.download_file(s3_url)
            local_files.append(local_path)
        except Exception as e:
            logger.error(f"Error downloading {s3_url}: {e}")

    logger.success(f"Processing dataset complete. Files saved to {output_dir}")
    return local_files


def convert_non_text_to_text(
    input_paths: List[Path],
    output_dir: Path = settings.INTERIM_DATA_DIR
) -> List[Path]:
    """
    Converts audio/video files to text and saves them as .txt files.

    :param input_paths: List of local paths to audio/video files.
    :param output_dir: Directory where resulting .txt files will be saved.
    :return: List of paths to created text files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_files = []

    for path in tqdm(input_paths, desc="Converting media to text"):
        ext = path.suffix.lower()[1:]

        try:
            if ext in AUDIO_FORMATS:
                text = transcribator.transcribe_audio(path)
            elif ext in VIDEO_FORMATS:
                text = transcribator.transcribe_video(path)
            else:
                logger.warning(f"Skipping unsupported file type: {path.name}")
                continue

            out_path = output_dir / (path.stem + ".txt")
            out_path.write_text(text, encoding="utf-8")
            output_files.append(out_path)

        except Exception as e:
            logger.error(f"Error converting {path.name}: {e}")

    return output_files


def build_dataset(
    input_dir: Path = settings.INTERIM_DATA_DIR,
    output_file: Path = settings.PROCESSED_DATA_DIR / "dataset.txt"
) -> Path:
    """
    Combine all .txt files into a single file for fine-tuning.

    :param input_dir: Directory with .txt files.
    :param output_file: Path to the output dataset file.
    :return: Path to the resulting dataset.
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)

    text_files = list(input_dir.glob("*.txt"))
    with output_file.open("w", encoding="utf-8") as f_out:
        for file in text_files:
            text = file.read_text(encoding="utf-8").strip()
            if text:
                f_out.write(text + "\n")

    logger.success(f"Dataset saved at {output_file}")
    return output_file
