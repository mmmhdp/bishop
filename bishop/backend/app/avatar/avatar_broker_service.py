import uuid

from sqlmodel import select

from app.train_material.TrainMaterial import TrainMaterial
from app.common.logging_service import logger
from app.common.config import settings
from app.common.api_deps import SessionDep, ProducerDep


async def send_train_start_message(
    session: SessionDep,
    producer: ProducerDep,
    avatar_id: uuid.UUID,
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
        "train_materials": materials_data,
    }

    logger.info(f"Sending START training message for avatar {avatar_id}")
    await producer.send(topic=settings.KAFKA_TOPIC_TRAIN, data=payload)


async def send_train_stop_message(
    producer: ProducerDep,
    avatar_id: uuid.UUID,
):
    """
    Sends a 'train_stop' message for the avatar.
    """
    payload = {
        "event": "train_stop",
        "avatar_id": str(avatar_id),
    }

    logger.info(f"Sending STOP training message for avatar {avatar_id}")
    await producer.send(topic=settings.KAFKA_TOPIC_TRAIN, data=payload)
