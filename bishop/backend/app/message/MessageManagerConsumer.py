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
            event = task_data["event"]
            logger.info(f"Received task from {msg.topic}: {task_data}")
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON message")
            return

        async with db_context() as session:
            message_id = task_data["message_id"]

            db_message = await message_repository.get_message_by_id(
                session=session,
                message_id=message_id
            )
            if db_message is None:
                logger.warning(f"Message with ID {message_id} not found.")
                return

            if event == "save_response":
                db_message.text = task_data.get(
                    "generated_text", db_message.text
                )
                db_message.text_status = "ready"

            elif event == "save_response_dub":
                db_message.text = task_data.get(
                    "generated_text", db_message.text
                )
                db_message.text_status = "ready"
                db_message.dub_url = task_data.get(
                    "dub_url", db_message.dub_url
                )
                db_message.dub_status = "ready"

            session.add(db_message)
            await session.commit()
