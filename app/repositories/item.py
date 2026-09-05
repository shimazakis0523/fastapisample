from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item


class ItemRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, item_id: int) -> Item | None:
        return await self._session.get(Item, item_id)

    async def list(self, *, limit: int, offset: int) -> list[Item]:
        stmt = select(Item).order_by(Item.id).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, item: Item) -> Item:
        self._session.add(item)
        await self._session.flush()
        await self._session.refresh(item)
        return item

    async def delete(self, item: Item) -> None:
        await self._session.delete(item)
        await self._session.flush()
