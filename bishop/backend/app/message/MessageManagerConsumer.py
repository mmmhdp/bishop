import json
from app.common.logging_service import logger
from app.broker.Consumer import KafkaMessageConsumer


class MessageManagerConsumer(KafkaMessageConsumer):

    def __init__(self, topics, bootstrap_servers, group_id, restart_delay=5):
        super().__init__(topics, bootstrap_servers, group_id, restart_delay)

    async def process_message(self, msg):
        try:
            task_data = json.loads(msg.value.decode("utf-8"))
            logger.info(f"Received task from {msg.topic}: {task_data}")
            # Insert your logic here
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON message")

