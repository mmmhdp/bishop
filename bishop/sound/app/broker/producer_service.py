import uuid

from app.broker.Producer import KafkaMessageProducer
from app.common.logging_service import logger
from app.common.config import settings

EVENTS = {
    "save_response_dub": "save_response_dub",
}


def send_update_message_state(
    producer: KafkaMessageProducer,
    message_id: uuid.UUID,
    generated_text: str,
    dub_url: str,
):
    """
    Sends a 'generate_response' message for the avatar.
    """
    payload = {
        "event": EVENTS["save_response_dub"],
        "message_id": str(message_id),
        "dub_url": dub_url,
        "generated_text": generated_text,
    }

    logger.info(f"Sending generate_response message: {payload}")
    producer.send(topic=settings.KAFKA_TOPIC_SAVE_RESPONSE_DUB, data=payload)
