import uuid
from typing import Any

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.user.User import User
from app.transcription.Transcription import (
    Transcription,
    SourceType
)

async def create_transcription(
        *,
        session: AsyncSession,
        text: str,
        owner_id: uuid.UUID,
        original_source: SourceType,
        owner: User) -> Transcription:

    transcription = Transcription(
        text=text,
        original_source=original_source,
        owner_id=owner_id,
        owner=owner
    )
    session.add(transcription)
    await session.commit()
    await session.refresh(transcription)
    return transcription