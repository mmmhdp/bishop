import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from app.chat import chat_repository
from app.chat.Chat import ChatCreate, ChatUpdate
from app.tests.utils.avatar import create_random_avatar
from app.tests.utils.utils import random_lower_string


@pytest.mark.asyncio
async def test_create_chat(db: AsyncSession):
    avatar = await create_random_avatar(db)
    title = random_lower_string()
    chat = await chat_repository.create_chat(
        session=db,
        chat_create=ChatCreate(title=title),
        avatar_id=avatar.id,
    )
    assert chat.id is not None
    assert chat.avatar_id == avatar.id
    assert chat.title == title


@pytest.mark.asyncio
async def test_is_chat_exists_for_avatar(db: AsyncSession):
    avatar = await create_random_avatar(db)
    title = random_lower_string()
    await chat_repository.create_chat(
        session=db,
        chat_create=ChatCreate(title=title),
        avatar_id=avatar.id,
    )
    existing_chat = await chat_repository.is_chat_exists_for_avatar(
        session=db,
        avatar_id=avatar.id,
        chat_create=ChatCreate(title=title),
    )
    assert existing_chat is not None
    assert existing_chat.title == title


@pytest.mark.asyncio
async def test_get_chat_by_id(db: AsyncSession):
    avatar = await create_random_avatar(db)
    title = random_lower_string()
    chat = await chat_repository.create_chat(
        session=db,
        chat_create=ChatCreate(title=title),
        avatar_id=avatar.id,
    )
    fetched = await chat_repository.get_chat_by_id(
        session=db,
        chat_id=chat.id,
    )
    assert fetched is not None
    assert fetched.id == chat.id


@pytest.mark.asyncio
async def test_get_chats_for_avatar(db: AsyncSession):
    avatar = await create_random_avatar(db)
    await chat_repository.create_chat(
        session=db,
        chat_create=ChatCreate(title=random_lower_string()),
        avatar_id=avatar.id,
    )
    await chat_repository.create_chat(
        session=db,
        chat_create=ChatCreate(title=random_lower_string()),
        avatar_id=avatar.id,
    )
    chats = await chat_repository.get_chats_for_avatar(
        session=db,
        avatar_id=avatar.id,
    )
    assert len(chats) >= 2
    for chat in chats:
        assert chat.avatar_id == avatar.id


@pytest.mark.asyncio
async def test_update_chat(db: AsyncSession):
    avatar = await create_random_avatar(db)
    original_title = random_lower_string()
    updated_title = random_lower_string()
    chat = await chat_repository.create_chat(
        session=db,
        chat_create=ChatCreate(title=original_title),
        avatar_id=avatar.id,
    )
    updated = await chat_repository.update_chat(
        session=db,
        chat_id=chat.id,
        chat_update=ChatUpdate(title=updated_title),
    )
    assert updated.title == updated_title


@pytest.mark.asyncio
async def test_delete_chat(db: AsyncSession):
    avatar = await create_random_avatar(db)
    chat = await chat_repository.create_chat(
        session=db,
        chat_create=ChatCreate(title=random_lower_string()),
        avatar_id=avatar.id,
    )
    result = await chat_repository.delete_chat(session=db, chat_id=chat.id)
    assert result is True
    deleted = await chat_repository.get_chat_by_id(session=db, chat_id=chat.id)
    assert deleted is None
