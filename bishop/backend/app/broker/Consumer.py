from aiokafka import AIOKafkaConsumer
import asyncio
import json
from app.common.logging_service import logger


class KafkaMessageConsumer:
    def __init__(self, topics, bootstrap_servers, group_id, restart_delay=5):
        self.topics = topics if isinstance(topics, list) else [topics]
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.restart_delay = restart_delay

        self.consumer: AIOKafkaConsumer | None = None
        self._running = False

    async def start(self):
        self._running = True
        while self._running:
            try:
                self.consumer = AIOKafkaConsumer(
                    *self.topics,
                    bootstrap_servers=self.bootstrap_servers,
                    group_id=self.group_id,
                    enable_auto_commit=False,
                    auto_offset_reset="earliest"
                )
                await self.consumer.start()
                logger.info(f"Subscribed to topics: {self.topics}")

                async for msg in self.consumer:
                    try:
                        await self.process_message(msg)
                        await self.consumer.commit()
                    except Exception as e:
                        logger.exception(f"Error processing message: {e}")
                        await asyncio.sleep(1)

                    if not self._running:
                        break

            except Exception as e:
                logger.exception(f"Consumer error: {e}. Restarting after {
                                 self.restart_delay} seconds...")
                await asyncio.sleep(self.restart_delay)

            finally:
                if self.consumer:
                    await self.consumer.stop()
                    logger.info("Consumer stopped.")

    async def stop(self):
        self._running = False
        if self.consumer:
            await self.consumer.stop()
            logger.info("Consumer stopped by shutdown event.")

    async def process_message(self, msg):
        try:
            task_data = json.loads(msg.value.decode("utf-8"))
            logger.info(f"Received task from {msg.topic}: {task_data}")
            # Insert your logic here
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON message")

