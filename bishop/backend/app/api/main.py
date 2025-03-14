from fastapi import APIRouter

from app.login import login_controller
from app.user import user_controller
from app.item import item_controller
from app.common import mixin_controller
from app.chat_message import chat_message_controller

api_router = APIRouter()

api_router.include_router(login_controller.router, tags=["login"])

api_router.include_router(user_controller.router,
                          prefix="/users", tags=["users"])

api_router.include_router(item_controller.router,
                          prefix="/items", tags=["items"])

api_router.include_router(mixin_controller.router,
                          prefix="/utils", tags=["utils"])

api_router.include_router(chat_message_controller.router,
                          prefix="/msgs", tags=["msgs"])
