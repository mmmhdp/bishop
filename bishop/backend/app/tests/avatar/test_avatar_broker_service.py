import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.avatar import avatar_broker_service
from app.train_material.TrainMaterial import TrainMaterial


@pytest.mark.asyncio
@patch("app.avatar.avatar_broker_service.settings.KAFKA_TOPIC_TRAIN", "train")
async def test_send_train_start_message():
    avatar_id = uuid.uuid4()

    mock_session = MagicMock()
    mock_exec_result = MagicMock()
    mock_exec_result.all.return_value = [
        TrainMaterial(id=uuid.uuid4(), avatar_id=avatar_id,
                      title="Doc 1", url="http://one.com", is_trained_on=False),
        TrainMaterial(id=uuid.uuid4(), avatar_id=avatar_id,
                      title="Doc 2", url="http://two.com", is_trained_on=False),
    ]
    mock_session.exec = AsyncMock(return_value=mock_exec_result)

    mock_producer = MagicMock()
    mock_producer.send = AsyncMock()

    await avatar_broker_service.send_train_start_message(
        session=mock_session,
        producer=mock_producer,
        avatar_id=avatar_id,
    )

    mock_producer.send.assert_awaited_once()
    args = mock_producer.send.call_args.kwargs

    assert args["topic"] == "train"
    assert args["data"]["event"] == "train_start"
    assert args["data"]["avatar_id"] == str(avatar_id)
    assert len(args["data"]["train_materials"]) == 2


@pytest.mark.asyncio
@patch("app.avatar.avatar_broker_service.settings.KAFKA_TOPIC_TRAIN", "train")
async def test_send_train_stop_message():
    avatar_id = uuid.uuid4()

    mock_producer = MagicMock()
    mock_producer.send = AsyncMock()

    await avatar_broker_service.send_train_stop_message(
        producer=mock_producer,
        avatar_id=avatar_id,
    )

    mock_producer.send.assert_awaited_once()
    args = mock_producer.send.call_args.kwargs

    assert args["topic"] == "train"
    assert args["data"]["event"] == "train_stop"
    assert args["data"]["avatar_id"] == str(avatar_id)
