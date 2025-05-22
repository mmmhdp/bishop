from typing import Any
import uuid
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.common.api_deps import (
    SessionDep,
    CurrentUser,
    ProducerDep,
    S3Dep,
)
from app.message.Message import (
    Message,
    MessageCreate,
    MessagePublic,
    MessagesPublic,
    MessageUpdate
)
from app.avatar.Avatar import Avatar
from app.common.models.SimpleMessage import SimpleMessage
from app.common.logging_service import logger
from app.common.config import settings
from app.message import message_repository
from app.message import message_broker_service
from app.broker.broker_utils import get_object_key_from_url


router = APIRouter()


@router.get("/", response_model=MessagesPublic)
async def read_messages(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    avatar_id: uuid.UUID,
    chat_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve messages for a specific chat.
    """
    messages = await message_repository.get_messages_for_chat(
        session=session, chat_id=chat_id, skip=skip, limit=limit
    )
    return MessagesPublic(data=messages, count=len(messages))


@router.get("/{message_id}", response_model=MessagePublic)
async def read_message(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    message_id: uuid.UUID
) -> Any:
    """
    Get a specific message from a chat.
    """
    message = await session.get(Message, message_id)
    if not message:
        raise HTTPException(
            status_code=404, detail="Message not found")
    return message


@router.post("/", response_model=MessagePublic)
async def create_message(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    avatar_id: uuid.UUID,
    chat_id: uuid.UUID,
    item_in: MessageCreate,
    producer: ProducerDep
) -> Any:
    """
    Create a new message in a specific chat.
    """
    message, rsp_msg = await message_repository.create_message(
        session=session,
        current_user=current_user,
        avatar_id=avatar_id,
        chat_id=chat_id,
        item_in=item_in
    )

    await message_broker_service.send_generate_response_message(
        producer=producer,
        message_id=rsp_msg.id,
        user_message=message.text
    )

    return rsp_msg


@router.put("/{message_id}", response_model=MessagePublic)
async def update_message(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    message_id: uuid.UUID,
    item_in: MessageUpdate
) -> Any:
    """
    Update a message.
    """
    message = await session.get(Message, message_id)
    if not message:
        raise HTTPException(
            status_code=404, detail="Base message for update is not found")

    update_dict = item_in.model_dump(exclude_unset=True)
    message.sqlmodel_update(update_dict)
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


@router.delete("/{message_id}")
async def delete_message(
    *,
    session: SessionDep,
    message_id: uuid.UUID
) -> SimpleMessage:
    """
    Delete a message.
    """
    message = await session.get(Message, message_id)
    if not message:
        raise HTTPException(
            status_code=404, detail="Message not found")

    await session.delete(message)
    await session.commit()

    return SimpleMessage(message="Message deleted successfully")


@router.get("/{rsp_msg_id}/response/")
async def get_avatar_response(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    avatar_id: uuid.UUID,
    chat_id: uuid.UUID,
    rsp_msg_id: uuid.UUID,
) -> Message:

    rsp_msg = await session.get(Message, rsp_msg_id)
    if not rsp_msg:
        raise HTTPException(
            status_code=422, detail="Response message is not exists")

    if not rsp_msg.text:
        raise HTTPException(
            status_code=404, detail="Response is not ready yet")

    return rsp_msg


@router.get("/{rsp_msg_id}/response/dub/")
async def get_avatar_response_dub_stream(
    *,
    session: SessionDep,
    S3: S3Dep,
    current_user: CurrentUser,
    avatar_id: uuid.UUID,
    chat_id: uuid.UUID,
    rsp_msg_id: uuid.UUID,
    producer: ProducerDep,
) -> StreamingResponse:

    logger.info(f"[get_avatar_response_dub_stream] Called with avatar_id={
                avatar_id}, chat_id={chat_id}, rsp_msg_id={rsp_msg_id}, user_id={current_user.id}")

    # Fetch response message
    rsp_msg = await session.get(Message, rsp_msg_id)
    logger.info(
        f"[get_avatar_response_dub_stream] Fetched response message: {rsp_msg}")

    if not rsp_msg:
        logger.warning(f"[get_avatar_response_dub_stream] Message {
                       rsp_msg_id} not found in DB")
        raise HTTPException(
            status_code=422, detail="Response message does not exist"
        )

    if rsp_msg.text_status != "ready":
        logger.warning(f"[get_avatar_response_dub_stream] Message {
                       rsp_msg_id} text_status={rsp_msg.text_status} (expected 'ready')")
        raise HTTPException(
            status_code=404, detail="Response is not ready yet"
        )

    if not rsp_msg.dub_status:
        logger.error(f"[get_avatar_response_dub_stream] Message {
                     rsp_msg_id} dub_status is empty or corrupted: {rsp_msg.dub_status}")
        raise HTTPException(
            status_code=500, detail=f"Dub status is corrupted: {rsp_msg.dub_status}"
        )

    elif rsp_msg.dub_status == "pending":
        logger.info(f"[get_avatar_response_dub_stream] Dub is pending. Sending message to broker for generation. Message ID: {
                    rsp_msg.id}")

        storage_path = f"users/{current_user.id}/avatars/{
            avatar_id}/messages/{rsp_msg.id}"
        logger.debug(f"[get_avatar_response_dub_stream] Storage path: {storage_path}, Base voice URL: {
                     rsp_msg.avatar.voice_url if hasattr(rsp_msg, 'avatar') else 'N/A'}")

        rsp_msg_avatar = await session.get(Avatar, avatar_id)
        logger.debug(f"[get_avatar_response_dub_stream] voice_url: {
                     rsp_msg_avatar.voice_url}")

        logger.debug(f"[get_avatar_response_dub_stream] Base voice URL: {
                     rsp_msg_avatar.voice_url}")

        logger.debug(f"[get_avatar_response_dub_stream] Base voice url type: {
                     type(rsp_msg_avatar.voice_url)}")

        base_voice_url = get_object_key_from_url(
            rsp_msg_avatar.voice_url,
            settings.MINIO_BUCKET
        )

        # base_voice_url = None

        await message_broker_service.generate_dub_for_message(
            producer=producer,
            gen_message=rsp_msg.text,
            message_id=rsp_msg.id,
            storage_url=storage_path,
            base_voice_url=base_voice_url,
        )

        logger.info(
            f"[get_avatar_response_dub_stream] Sent dub generation request to Kafka. Updating message status to 'processing'.")

        rsp_msg = await message_repository.update_message_response(
            session=session,
            message_id=rsp_msg.id,
            dub_status="processing"
        )

        raise HTTPException(
            status_code=404,
            detail="Dub generation called first time. Wait for completion"
        )

    elif rsp_msg.dub_status == "processing":
        logger.info(f"[get_avatar_response_dub_stream] Dub is currently processing. Message ID: {
                    rsp_msg.id}")
        raise HTTPException(
            status_code=404,
            detail="Dub URL is in processing and not set yet"
        )

    # Parse dub_url
    try:
        logger.debug(f"[get_avatar_response_dub_stream] Extracting object name from URL: {
                     rsp_msg.dub_url}")
        obj_name = rsp_msg.dub_url
        logger.info(
            f"[get_avatar_response_dub_stream] MinIO object key: {obj_name}")
    except ValueError as e:
        logger.error(f"[get_avatar_response_dub_stream] Invalid dub_url format: {
                     rsp_msg.dub_url}, Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    # Fetch audio stream from MinIO
    try:
        logger.info(f"[get_avatar_response_dub_stream] Attempting to fetch object '{
                    obj_name}' from MinIO bucket '{settings.MINIO_BUCKET}'")
        response = S3.get_object(settings.MINIO_BUCKET, obj_name)
        logger.info(f"[get_avatar_response_dub_stream] Audio object retrieved successfully for message ID: {
                    rsp_msg.id}")
    except Exception as e:
        logger.error(f"[get_avatar_response_dub_stream] Failed to retrieve audio from S3. Bucket: {
                     settings.MINIO_BUCKET}, Object: {obj_name}, Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch audio: {str(e)}"
        )

    return StreamingResponse(response, media_type="audio/mpeg")
