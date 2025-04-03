import uuid

from app.broker.producer.Producer import KafkaMessageProducer
from app.common.logging_service import logger
from app.common.config import settings

EVENTS = {
    "inference_response": "inference_response",
}


async def send_generate_response_message(
    producer: KafkaMessageProducer,
    message_id: uuid.UUID,
    user_message: str = None

):
    """
    Sends a 'generate_response' message for the avatar.
    """
    payload = {
        "event": EVENTS["inference_response"],
        "message_id": str(message_id),
        "user_message": user_message
    }

    logger.info(f"Sending generate_response message: {payload}")
    await producer.send(topic=settings.KAFKA_TOPIC_LLM_INFERENCE, data=payload)
