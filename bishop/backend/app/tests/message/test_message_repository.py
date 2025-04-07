import uuid

import pytest
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from redis.asyncio import Redis as AsyncRedis

from app.chat.Chat import Chat
from app.avatar.Avatar import Avatar
from app.message import message_repository
from app.message.Message import MessageCreate
from app.tests.utils.chat import create_random_chat


@pytest.mark.asyncio
async def test_create_message(db: AsyncSession):
    chat = await create_random_chat(db)
    data = MessageCreate(text="Ping")

    result = await db.exec(
        select(Chat)
        .options(selectinload(Chat.avatar).selectinload(Avatar.user))
        .where(Chat.id == chat.id)
    )
    chat_with_preloads = result.scalar_one()

    message, rsp_msg = await message_repository.create_message(
        session=db,
        current_user=chat_with_preloads.avatar.user,
        avatar_id=chat_with_preloads.avatar_id,
        chat_id=chat_with_preloads.id,
        item_in=data,
    )

    assert message.text == data.text
    assert message.chat_id == chat_with_preloads.id
    assert message.avatar_id == chat_with_preloads.avatar_id
    assert message.user_id == chat_with_preloads.avatar.user_id

    assert rsp_msg.is_generated is True
    assert rsp_msg.text is None


@pytest.mark.asyncio
async def test_get_messages_for_chat(db: AsyncSession):
    chat = await create_random_chat(db)

    result = await db.exec(
        select(Chat)
        .options(selectinload(Chat.avatar).selectinload(Avatar.user))
        .where(Chat.id == chat.id)
    )
    chat_with_preloads = result.scalar_one()

    await message_repository.create_message(
        session=db,
        current_user=chat_with_preloads.avatar.user,
        avatar_id=chat_with_preloads.avatar.id,
        chat_id=chat_with_preloads.id,
        item_in=MessageCreate(text="First message"),
    )
    await message_repository.create_message(
        session=db,
        current_user=chat_with_preloads.avatar.user,
        avatar_id=chat_with_preloads.avatar.id,
        chat_id=chat_with_preloads.id,
        item_in=MessageCreate(text="Second message"),
    )

    messages = await message_repository.get_messages_for_chat(
        session=db,
        chat_id=chat_with_preloads.id
    )

    assert isinstance(messages, list)
    assert len(messages) >= 2
    texts = [m.text for m in messages]
    assert "First message" in texts
    assert "Second message" in texts


@pytest.mark.asyncio
async def test_get_response_id_by_msg_id_not_found(cache_client: AsyncRedis):
    message_id = uuid.uuid4()

    result = await message_repository.get_response_id_by_msg_id(
        cache_db=cache_client,
        message_id=message_id
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_response_id_by_msg_id_found(cache_client: AsyncRedis):
    message_id = uuid.uuid4()
    response_id = uuid.uuid4()

    await cache_client.set(str(message_id), str(response_id))

    result = await message_repository.get_response_id_by_msg_id(
        cache_db=cache_client,
        message_id=message_id
    )

    assert isinstance(result, uuid.UUID)
    assert result == response_id

    await cache_client.delete(str(message_id))
