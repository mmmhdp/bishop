import uuid

from app.common.logging_service import logger
from app.common.config import settings
from app.common.api_deps import ProducerDep
from app.message.message_repository import update_message_response

EVENTS = {
    "inference_response": "inference_response",
    "sound_inference": "sound_inference",
}


async def send_generate_response_message(
    producer: ProducerDep,
    message_id: uuid.UUID,
    user_message: str = None

):
    """
    Sends a 'generate_response' message for the avatar.
    """
    payload = {
        "event": EVENTS["inference_response"],
        "message_id": str(message_id),
        "text": user_message,
    }

    logger.info(f"Sending generate_response message: {payload}")
    await producer.send(topic=settings.KAFKA_TOPIC_LLM_INFERENCE, data=payload)


async def generate_dub_for_message(
    producer: ProducerDep,
    storage_url: str,
    message_id: uuid.UUID,
    base_voice_url: str = None,
    gen_message: str = None
):
    """
    Sends a 'generate_dub' message for the avatar.
    """
    payload = {
        "event": EVENTS["sound_inference"],
        "storage_url": storage_url,
        "base_voice_url": base_voice_url,
        "message_id": str(message_id),
        "text": gen_message,
    }

    logger.info(f"Sending generate_dub message: {payload}")
    await producer.send(topic=settings.KAFKA_TOPIC_SOUND_INFERENCE, data=payload)
