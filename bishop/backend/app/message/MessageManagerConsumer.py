import json
from contextlib import asynccontextmanager

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.logging_service import logger
from app.broker.Consumer import KafkaMessageConsumer
from app.message import message_repository
from app.common.db import async_engine
from app.common.logging_service import logger


@asynccontextmanager
async def db_context():
    async with AsyncSession(async_engine) as session:
        yield session


class MessageManagerConsumer(KafkaMessageConsumer):

    def __init__(self, topics, bootstrap_servers, group_id, restart_delay=5):
        super().__init__(topics, bootstrap_servers, group_id, restart_delay)

    async def process_message(self, msg):
        try:
            task_data = json.loads(msg.value.decode("utf-8"))
            logger.info(f"Received task from {msg.topic}: {task_data}")

            async with db_context() as session:
                message_id = task_data["message_id"]
                generated_text = task_data["generated_text"]
                dub_url = task_data["dub_url"]
                await message_repository.update_message_response(
                    session=session,
                    message_id=message_id,
                    text=generated_text,
                    dub_url=dub_url
                )

        except json.JSONDecodeError:
            logger.error("Failed to decode JSON message")
