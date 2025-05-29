import uuid

from sqlmodel import select

from app.train_material.TrainMaterial import TrainMaterial
from app.common.logging_service import logger
from app.common.config import settings
from app.common.api_deps import SessionDep, ProducerDep
from app.avatar import avatar_repository

EVENTS = {
    "train_start": "train_start",
    "train_stop": "train_stop",
}


async def send_train_start_message(
    session: SessionDep,
    producer: ProducerDep,
    avatar_id: uuid.UUID,
):
    """
    Sends a 'train_start' message including all untrained materials for the avatar.
    """
    untrained_materials = await avatar_repository.get_avaliable_train_materials(
        session=session,
        avatar_id=avatar_id
    )

    logger.info(
        f"Found {untrained_materials.count} untrained materials for avatar {avatar_id}")

    materials_data = [
        {
            "id": str(material.id),
            "type": material.type,
            "url": material.url
        }
        for material in untrained_materials.data
    ]

    payload = {
        "event": EVENTS["train_start"],
        "avatar_id": str(avatar_id),
        "train_materials": materials_data,
    }

    logger.info(f"Sending START training message for avatar {avatar_id}")
    msg = await producer.send(topic=settings.KAFKA_TOPIC_LLM_TRAIN, data=payload)

    logger.info(f"Message sent: {msg}")
    invalidated_materials = await avatar_repository.invalidate_train_materials(
        session=session,
        avatar_id=avatar_id
    )
    logger.info(f"Invalidated {invalidated_materials.count
                               } materials for avatar {avatar_id}")


async def send_train_stop_message(
    producer: ProducerDep,
    avatar_id: uuid.UUID,
):
    """
    Sends a 'train_stop' message for the avatar.
    """
    payload = {
        "event": EVENTS["train_stop"],
        "avatar_id": str(avatar_id),
    }

    logger.info(f"Sending STOP training message for avatar {avatar_id}")
    await producer.send(topic=settings.KAFKA_TOPIC_LLM_TRAIN, data=payload)
