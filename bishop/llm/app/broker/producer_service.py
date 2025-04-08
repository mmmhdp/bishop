import uuid

from app.broker.Producer import KafkaMessageProducer
from app.common.logging_service import logger
from app.common.config import settings

EVENTS = {
    "inference_response": "inference_response",
    "save_response": "save_response",
}


def send_generate_response_message(
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
    producer.send(topic=settings.KAFKA_TOPIC_LLM_INFERENCE, data=payload)


def send_update_message_state(
    producer: KafkaMessageProducer,
    message_id: uuid.UUID,
    user_message: str = None

):
    """
    Sends a 'generate_response' message for the avatar.
    """
    payload = {
        "event": EVENTS["save_response"],
        "message_id": str(message_id),
        "user_message": user_message
    }

    logger.info(f"Sending generate_response message: {payload}")
    producer.send(topic=settings.KAFKA_TOPIC_SAVE_RESPONSE, data=payload)
