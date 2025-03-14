from app.item.Item import Item, ItemCreate
import uuid
from sqlmodel.ext.asyncio.session import AsyncSession


async def create_item(
        *,
        session: AsyncSession,
        item_in: ItemCreate,
        owner_id: uuid.UUID) -> Item:

    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return db_item
