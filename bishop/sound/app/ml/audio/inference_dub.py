import io
import os
import torch
import tempfile

from app.common.db import minio_client
from app.common.logging_service import logger
from app.broker.producer_service import send_update_message_state
from app.broker.Producer import KafkaMessageProducer
from app.common.config import settings
from TTS.api import TTS


def download_minio_file_to_local(object_name: str, suffix: str = ".wav") -> str:
    """
    Downloads a file from MinIO and saves it as a temporary file locally.

    Args:
        object_name (str): The key of the object in the MinIO bucket.
        suffix (str): The file extension to use for the temporary file.

    Returns:
        str: The path to the temporary local file.
    """
    logger.debug(f"Downloading object '{object_name}' from MinIO.")
    try:
        response = minio_client.get_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=object_name,
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(response.read())
            temp_path = temp_file.name

        logger.info(f"Downloaded '{
                    object_name}' to temporary file '{temp_path}'.")
        return temp_path
    except Exception as e:
        logger.error(f"Failed to download object '{
                     object_name}' from MinIO: {e}")
        raise


def delete_local_file(file_path: str) -> None:
    """
    Deletes a local file if it exists.

    Args:
        file_path (str): Path to the local file to delete.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted temporary file: {file_path}")
        else:
            logger.warning(f"Tried to delete non-existent file: {file_path}")
    except Exception as e:
        logger.error(f"Error deleting file '{file_path}': {e}")
        raise


class BytesIOWrapper:
    def __init__(self, buf):
        self.buffer = buf

    def write(self, data):
        logger.debug(f"Writing {len(data)} bytes to buffer.")
        return self.buffer.write(data)

    def flush(self):
        logger.debug("Flushing buffer.")
        return self.buffer.flush()


os.environ["COQUI_TOS_AGREED"] = "1"
# Log device information
device = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Selected device for TTS inference: {device}")

# Initialize Kafka producer
producer = KafkaMessageProducer(
    bootstrap_servers=settings.KAFKA_BROKER_URL,
)
logger.info("Kafka producer initialized.")

# Load the TTS model once
logger.info("Loading TTS model...")
try:
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    logger.info("TTS model loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load TTS model: {e}")
    raise


def save_dub_to_s3(dub_url, buffer):
    buffer.seek(0)  # Ensure start of stream
    buffer_size = buffer.getbuffer().nbytes
    logger.debug(f"Uploading buffer to S3. Size: {
                 buffer_size} bytes. URL: {dub_url}")

    try:
        minio_client.put_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=dub_url,
            data=buffer,
            length=buffer_size,
            content_type='audio/wav'
        )
        logger.info(f"Audio file successfully uploaded to S3 at {dub_url}")
    except Exception as e:
        logger.error(f"Failed to upload audio to S3: {e}")
        raise

    return dub_url


def process_inference_task(task_data):
    logger.debug(f"Received task_data: {task_data}")

    input_text = task_data["text"]
    msg_id = task_data["message_id"]
    dub_url = task_data["storage_url"]
    base_voice_url = task_data["base_voice_url"]

    # Download the base voice file from MinIO

    logger.info(f"Processing inference task for message_id: {msg_id}")

    try:
        # Prepare buffer and wrapper
        dub_buffer = io.BytesIO()
        wrapped_buffer = BytesIOWrapper(dub_buffer)

        logger.debug("Starting TTS synthesis...")
        if base_voice_url is None or base_voice_url == "":
            logger.debug("No base voice URL provided, using default voice.")
            tts.tts_to_file(
                text=input_text,
                language="ru",
                pipe_out=wrapped_buffer,
                speaker="Craig Gutsy"
            )
        else:
            base_voice_path = download_minio_file_to_local(base_voice_url)
            tts.tts_to_file(
                text=input_text,
                language="ru",
                pipe_out=wrapped_buffer,
                speaker_wav=base_voice_path,
            )
        logger.info("TTS synthesis complete.")

        # Save the generated dub to S3
        save_dub_to_s3(dub_url, dub_buffer)

        # Send the update
        logger.debug("Sending update message to Kafka...")
        send_update_message_state(
            producer=producer,
            message_id=msg_id,
            generated_text=input_text,
            dub_url=dub_url,
        )
        logger.info(
            f"Message {msg_id} processed and update sent successfully.")

    except Exception as e:
        logger.error(
            f"Error while processing inference task for message_id {msg_id}: {e}")
        raise

    finally:
        dub_buffer.close()
        if base_voice_url:
            logger.debug(f"Deleting local file: {base_voice_path}")
            delete_local_file(base_voice_path)
        logger.debug("Closed dub buffer.")
