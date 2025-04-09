import uuid

from app.common.logging_service import logger
from app.common.config import settings
from app.common.api_deps import ProducerDep
from app.message.message_repository import update_message_response

EVENTS = {
    "inference_response": "inference_response",
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
