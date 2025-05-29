from aiokafka import AIOKafkaProducer
import json
from app.common.logging_service import logger


class KafkaMessageProducer:
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.producer: AIOKafkaProducer | None = None

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers)
        await self.producer.start()
        logger.info("Kafka producer started.")

    async def stop(self):
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped.")

    async def send(self, topic: str, data: dict):
        if not self.producer:
            raise RuntimeError(
                "Producer is not started. Call `start()` first.")

        try:
            message = json.dumps(data).encode("utf-8")
            await self.producer.send(topic, message)
            logger.info(f"Sent message to topic '{topic}': {data}")
        except Exception as e:
            logger.exception(f"Failed to send message to topic '{topic}': {e}")

        return message

    async def flush(self):
        if self.producer:
            await self.producer.flush()
