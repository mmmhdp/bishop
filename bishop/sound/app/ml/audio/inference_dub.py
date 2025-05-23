import io
import os
import torch
import tempfile
import soundfile as sf

from app.common.db import minio_client
from app.common.logging_service import logger
from app.broker.producer_service import send_update_message_state
from app.broker.Producer import KafkaMessageProducer
from app.common.config import settings
from TTS.api import TTS
from transformers import AutoTokenizer, AutoModelForCausalLM
from xcodec2.modeling_xcodec2 import XCodec2Model  # adjust import as needed

# --- Common utilities ---


def download_minio_file_to_local(object_name: str, suffix: str = ".wav") -> str:
    logger.debug(f"[download_minio] Starting download for '{object_name}'")
    try:
        response = minio_client.get_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=object_name,
        )
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            data = response.read()
            logger.debug(f"[download_minio] Read {
                         len(data)} bytes from MinIO for '{object_name}'")
            temp_file.write(data)
            temp_path = temp_file.name
        logger.info(f"[download_minio] Downloaded '{
                    object_name}' to '{temp_path}'")
        return temp_path
    except Exception as e:
        logger.error(f"[download_minio] Failed to download '{
                     object_name}': {e}")
        raise


def delete_local_file(file_path: str) -> None:
    logger.debug(f"[cleanup] Attempting to delete local file: {file_path}")
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"[cleanup] Deleted temporary file: {file_path}")
        else:
            logger.warning(
                f"[cleanup] File not found for deletion: {file_path}")
    except Exception as e:
        logger.error(f"[cleanup] Error deleting file '{file_path}': {e}")
        raise


def save_dub_to_s3(dub_url: str, buffer: io.BytesIO) -> str:
    buffer.seek(0)
    size = buffer.getbuffer().nbytes
    logger.debug(f"[upload_s3] Uploading {size} bytes to S3 at '{dub_url}'")
    try:
        minio_client.put_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=dub_url,
            data=buffer,
            length=size,
            content_type='audio/wav'
        )
        logger.info(f"[upload_s3] Successfully uploaded audio to '{dub_url}'")
    except Exception as e:
        logger.error(f"[upload_s3] Failed to upload audio to '{dub_url}': {e}")
        raise
    return dub_url


class BytesIOWrapper:
    def __init__(self, buf):
        self.buffer = buf
        logger.debug("[wrapper] Initialized BytesIOWrapper")

    def write(self, data):
        logger.debug(f"[wrapper] Writing {len(data)} bytes to buffer")
        return self.buffer.write(data)

    def flush(self):
        logger.debug("[wrapper] Flushing buffer")
        return self.buffer.flush()


# --- Environment & Producer ---
os.environ["COQUI_TOS_AGREED"] = "1"
device = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"[init] Using device: {device}")
producer = KafkaMessageProducer(bootstrap_servers=settings.KAFKA_BROKER_URL)
logger.info("[init] Kafka producer initialized.")

# --- Lazy model placeholders ---
tts = None
llasa_tokenizer = None
llasa_model = None
codec_model = None

# --- Helper for LLASA tokens ---


def extract_speech_ids(tokens_str):
    logger.debug(
        f"[extract_ids] Extracting speech IDs from tokens: {tokens_str}")
    ids = []
    for t in tokens_str:
        if t.startswith('<|s_') and t.endswith('|>'):
            try:
                idx = int(t[4:-2])
                ids.append(idx)
            except ValueError:
                logger.warning(f"[extract_ids] Invalid token format: {t}")
    logger.info(f"[extract_ids] Extracted speech IDs: {ids}")
    return ids

# --- Model loaders ---


def init_tts_model():
    global tts
    if tts is None:
        logger.info("[init] Loading Coqui TTS model...")
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        logger.info("[init] Coqui TTS model loaded successfully.")
    return tts


def init_llasa_models():
    global llasa_tokenizer, llasa_model, codec_model
    if llasa_tokenizer is None or llasa_model is None or codec_model is None:
        llasa_repo = 'HKUSTAudio/Llasa-1B'
        codec_repo = 'HKUSTAudio/xcodec2'
        logger.info(f"[init] Loading LLASA model from '{llasa_repo}'")
        llasa_tokenizer = AutoTokenizer.from_pretrained(llasa_repo)
        llasa_model = AutoModelForCausalLM.from_pretrained(
            llasa_repo).eval().to(device)
        logger.info("[init] LLASA model loaded.")
        logger.info(f"[init] Loading Codec2 model from '{codec_repo}'")
        codec_model = XCodec2Model.from_pretrained(
            codec_repo).eval().to(device)
        logger.info("[init] Codec2 model loaded.")
    return llasa_tokenizer, llasa_model, codec_model

# --- Task Processors ---


def process_inference_task(task_data: dict) -> None:
    """Process a TTS inference task using Coqui TTS."""
    init_tts_model()
    msg_id = task_data['message_id']
    text = task_data['text']
    dub_url = task_data['storage_url']
    base_voice = task_data.get('base_voice_url', '')
    logger.info(f"[process_inference] Starting task {
                msg_id} with text length {len(text)}")
    logger.debug(f"[process_inference] Storage URL: {
                 dub_url}, Base voice URL: {base_voice}")

    buffer = io.BytesIO()
    wrapper = BytesIOWrapper(buffer)

    try:
        if base_voice:
            temp = download_minio_file_to_local(base_voice)
            logger.debug(
                f"[process_inference] Using custom voice from '{temp}'")
            tts.tts_to_file(text=text, language='ru',
                            speaker_wav=temp, pipe_out=wrapper)
        else:
            logger.debug(
                "[process_inference] Using default Coqui speaker 'Craig Gutsy'")
            tts.tts_to_file(text=text, language='ru',
                            speaker='Craig Gutsy', pipe_out=wrapper)
        logger.info(
            f"[process_inference] TTS synthesis complete for task {msg_id}")

        save_dub_to_s3(dub_url, buffer)
        logger.debug(f"[process_inference] Uploaded dub for task {msg_id}")

        send_update_message_state(
            producer, msg_id, generated_text=text, dub_url=dub_url)
        logger.info(f"[process_inference] Update sent for task {msg_id}")
    except Exception as e:
        logger.error(f"[process_inference] Error in task {msg_id}: {e}")
        raise
    finally:
        buffer.close()
        logger.debug(f"[process_inference] Closed buffer for task {msg_id}")
        if base_voice:
            delete_local_file(temp)


def process_llasa_task(task_data: dict) -> None:
    """Process a text-to-speech task using LLASA+Codec2."""
    llasa_tokenizer, llasa_model, codec_model = init_llasa_models()
    msg_id = task_data['message_id']
    text = task_data['text']
    dub_url = task_data['storage_url']
    logger.info(f"[process_llasa] Starting task {
                msg_id} with text length {len(text)}")

    buffer = io.BytesIO()
    try:
        formatted = f"<|TEXT_UNDERSTANDING_START|>{
            text}<|TEXT_UNDERSTANDING_END|>"
        logger.debug(f"[process_llasa] Formatted prompt: {formatted}")
        chat = [
            {"role": "user", "content": "Convert the text to speech:" + formatted},
            {"role": "assistant", "content": "<|SPEECH_GENERATION_START|>"}
        ]
        in_ids = llasa_tokenizer.apply_chat_template(
            chat, tokenize=True, return_tensors='pt', continue_final_message=True)
        in_ids = in_ids.to(device)
        logger.debug(f"[process_llasa] Input IDs shape: {in_ids.shape}")

        eos_id = llasa_tokenizer.convert_tokens_to_ids(
            '<|SPEECH_GENERATION_END|>')
        outputs = llasa_model.generate(
            in_ids,
            max_length=2048,
            eos_token_id=eos_id,
            do_sample=True,
            top_p=1,
            temperature=0.8
        )
        logger.info(f"[process_llasa] Generation complete for task {msg_id}")

        gen_ids = outputs[0][in_ids.shape[1]:-1]
        tok_strs = llasa_tokenizer.batch_decode(
            gen_ids, skip_special_tokens=True)
        logger.debug(f"[process_llasa] Decoded tokens: {tok_strs}")

        speech_ids = extract_speech_ids(tok_strs)
        logger.debug(f"[process_llasa] Speech IDs: {speech_ids}")

        codes = torch.tensor(speech_ids).cuda().unsqueeze(0).unsqueeze(0)
        wav = codec_model.decode_code(codes)
        logger.info(
            f"[process_llasa] Codec2 decoding complete for task {msg_id}")

        sf.write(buffer, wav[0, 0, :].cpu().numpy(), 16000, format='WAV')
        logger.debug(
            f"[process_llasa] WAV written to buffer for task {msg_id}")

        save_dub_to_s3(dub_url, buffer)
        send_update_message_state(
            producer, msg_id, generated_text=text, dub_url=dub_url)
        logger.info(f"[process_llasa] Update sent for task {msg_id}")
    except Exception as e:
        logger.error(f"[process_llasa] Error in task {msg_id}: {e}")
        raise
    finally:
        buffer.close()
        logger.debug(f"[process_llasa] Closed buffer for task {msg_id}")

# --- Dispatcher ---


def dispatch_task(task_data: dict) -> None:
    # mode = task_data.get('mode', 'tts')
    mode = None
    msg_id = task_data.get('message_id', 'unknown')
    logger.info(f"[dispatcher] Received task {msg_id} with mode '{mode}'")
    if mode == 'llasa':
        process_llasa_task(task_data)
    else:
        process_inference_task(task_data)
    logger.info(f"[dispatcher] Completed task {msg_id}")

