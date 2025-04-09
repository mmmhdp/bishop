from app.common.logging_service import logger
from app.common.config import settings
from app.broker.producer_service import send_update_message_state
from app.broker.Producer import KafkaMessageProducer


producer = KafkaMessageProducer(
    bootstrap_servers=settings.KAFKA_BROKER_URL,
)


def process_inference_task(task_data):
    print(task_data)
    message_id = task_data["message_id"]
    text = task_data["text"]
    generated_text = "dummy_text"
    dub_url = "fake_url"

    logger.info(f"Processing inference task with task_data: {task_data}")

    # generating logic call
    send_update_message_state(
        producer=producer,
        message_id=message_id,
        generated_text=generated_text,
        dub_url=dub_url
    )
