import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.broker.producer.Producer import KafkaMessageProducer
from app.train_material.TrainMaterial import TrainMaterial
from app.common.logging_service import logger
from app.common.config import settings


async def send_train_start_message(
    session: AsyncSession,
    producer: KafkaMessageProducer,
    avatar_id: uuid.UUID,
    user_id: Optional[uuid.UUID] = None
):
    """
    Sends a 'train_start' message including all untrained materials for the avatar.
    """
    statement = select(TrainMaterial).where(
        TrainMaterial.avatar_id == avatar_id,
        TrainMaterial.is_trained_on is False
    )
    result = await session.exec(statement)
    untrained_materials = result.all()

    logger.info(f"Found {len(untrained_materials)
                         } untrained materials for avatar {avatar_id}")

    materials_data = [
        {
            "id": str(material.id),
            "title": material.title,
            "url": material.url
        }
        for material in untrained_materials
    ]

    payload = {
        "event": "train_start",
        "avatar_id": str(avatar_id),
        "user_id": str(user_id) if user_id else None,
        "timestamp": datetime.utcnow().isoformat(),
        "train_materials": materials_data,
    }

    logger.info(f"Sending START training message for avatar {avatar_id}")
    producer.send(topic=settings.KAFKA_TOPIC_TRAIN, data=payload)


def send_train_stop_message(
    producer: KafkaMessageProducer,
    avatar_id: uuid.UUID,
    user_id: Optional[uuid.UUID] = None
):
    """
    Sends a 'train_stop' message for the avatar.
    """
    payload = {
        "event": "train_stop",
        "avatar_id": str(avatar_id),
        "user_id": str(user_id) if user_id else None,
        "timestamp": datetime.utcnow().isoformat(),
    }

    logger.info(f"Sending STOP training message for avatar {avatar_id}")
    producer.send(topic=settings.KAFKA_TOPIC_TRAIN, data=payload)

