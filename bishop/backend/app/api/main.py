from fastapi import APIRouter

from app.login import login_controller
from app.user import user_controller
from app.common import mixin_controller
from app.message import message_controller
from app.transcription import transcription_controller
from app.chat import chat_controller
from app.avatar import avatar_controller

api_router = APIRouter()

api_router.include_router(login_controller.router, tags=["login"])

api_router.include_router(user_controller.router,
                          prefix="/users", tags=["users"])

api_router.include_router(mixin_controller.router,
                          prefix="/utils", tags=["utils"])

api_router.include_router(message_controller.router,
                          prefix="/msgs", tags=["msgs"])

api_router.include_router(transcription_controller.router,
                          prefix="/upload", tags=["transcriptions"])

api_router.include_router(chat_controller.router,
                          prefix="/chat", tags=["chats"])

api_router.include_router(avatar_controller.router,
                          prefix="/avatar", tags=["avatars"])
