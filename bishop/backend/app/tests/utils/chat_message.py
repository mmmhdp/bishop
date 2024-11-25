from sqlmodel import Session

from app import crud
from app.models import ChatMessage, ChatMessageCreate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_chat_message(db: Session) -> ChatMessage:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    message = random_lower_string()
    item_in = ChatMessageCreate(message=message)
    return crud.create_chat_message(
        session=db,
        item_in=item_in,
        owner_id=owner_id
    )
