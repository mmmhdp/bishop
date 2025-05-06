import random
import re
from pathlib import Path
from typing import List
from unicodedata import normalize

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
        output_dir: Path = Path(settings.RAW_DATA_DIR),
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

    logger.info(f"Processing dataset complete. Files saved to {output_dir}")
    return local_files


def convert_non_text_to_text(
        input_paths: List[Path],
        output_dir: Path = Path(settings.INTERIM_DATA_DIR),
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
                out_path = transcribator.transcribe_audio(path, output_dir)
            elif ext in VIDEO_FORMATS:
                out_path = transcribator.transcribe_video(path, output_dir)
            else:
                logger.warning(f"Skipping unsupported file type: {path.name}")
                continue

            output_files.append(out_path)

        except Exception as e:
            logger.error(f"Error converting {path.name}: {e}")

    return output_files


def _clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _split_into_chunks(text: str, max_len: int = 1000, min_len: int = 50) -> list[str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    rough_chunks = re.split(r"\n{2,}|\.\s", text)
    refined_chunks = []

    for chunk in rough_chunks:
        chunk = chunk.strip()
        if len(chunk) < min_len:
            continue

        if not re.search(r"[.,!?…]", chunk):
            i = 0
            while i < len(chunk):
                max_rand_len = min(max_len, len(chunk) - i)
                if max_rand_len < min_len:
                    break
                rand_len = random.randint(min_len, min(max_len, len(chunk) - i))
                part = chunk[i:i + rand_len].strip()
                if len(part) >= min_len:
                    refined_chunks.append(part)
                i += rand_len
            continue

        while len(chunk) > max_len:
            split_idx = chunk.rfind(" ", 0, max_len)
            if split_idx == -1:
                split_idx = max_len
            part = chunk[:split_idx].strip()
            if len(part) >= min_len:
                refined_chunks.append(part)
            chunk = chunk[split_idx:].strip()
        if len(chunk) >= min_len:
            refined_chunks.append(chunk)

    return refined_chunks


def build_dataset(
    input_dir: Path = Path(settings.INTERIM_DATA_DIR),
    output_file: Path = Path(settings.PROCESSED_DATA_DIR) / "dataset.txt",
) -> Path:
    """
    Build a clean dataset for fine-tuning.
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)
    text_files = list(input_dir.glob("*.txt"))

    all_chunks = []

    for file in text_files:
        raw_text = file.read_text(encoding="utf-8")
        if not raw_text.strip():
            continue
        cleaned = _clean_text(raw_text)
        chunks = _split_into_chunks(cleaned)
        all_chunks.extend(chunks)

    unique_chunks = list(dict.fromkeys(all_chunks))

    with output_file.open("w", encoding="utf-8") as f_out:
        for chunk in unique_chunks:
            f_out.write(chunk + "\n")

    logger.info(f"Cleaned dataset with {len(unique_chunks)} samples saved at {output_file}")
    return output_file
