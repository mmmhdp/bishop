import uuid
import pytest
from unittest.mock import AsyncMock

from app.message import message_broker_service
from app.broker.producer.Producer import KafkaMessageProducer
from app.common.config import settings


@pytest.mark.asyncio
async def test_send_generate_response_message():
    mock_producer = AsyncMock(spec=KafkaMessageProducer)
    message_id = uuid.uuid4()
    user_message = "Ping"

    await message_broker_service.send_generate_response_message(
        producer=mock_producer,
        message_id=message_id,
        user_message=user_message
    )

    mock_producer.send.assert_called_once_with(
        topic=settings.KAFKA_TOPIC_LLM_INFERENCE,
        data={
            "event": "inference_response",
            "message_id": str(message_id),
            "user_message": user_message,
        }
    )
