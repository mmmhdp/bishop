from fastapi import APIRouter

from app.login import login_controller
from app.user import user_controller
from app.common import mixin_controller
from app.message import message_controller
from app.chat import chat_controller
from app.avatar import avatar_controller
from app.train_material import train_material_controller

api_router = APIRouter()

api_router.include_router(login_controller.router, tags=["login"])


api_router.include_router(mixin_controller.router,
                          prefix="/utils", tags=["utils"])


chat_controller.router.include_router(message_controller.router,
                                      prefix="/{chat_id}/msgs", tags=["msgs"])

avatar_controller.router.include_router(chat_controller.router,
                                        prefix="/{avatar_id}/chat", tags=["chats"])

avatar_controller.router.include_router(train_material_controller.router,
                                        prefix="/{avatar_id}/train", tags=["train"])

api_router.include_router(
    avatar_controller.router, prefix="/avatars", tags=["avatars"])

api_router.include_router(user_controller.router,
                          prefix="/users", tags=["users"])
