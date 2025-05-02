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

    generated_text = "Hello my friend. I am not a robot. I am a human being. At least I think so."
    generated_dub_url = None

    logger.info(f"Processing inference task with task_data: {task_data}")

    # generating logic call

    send_update_message_state(
        producer=producer,
        message_id=message_id,
        generated_text=generated_text,
        dub_url=generated_dub_url
    )
