from app.core.exceptions import ItemNotFoundError
from app.models.item import Item
from app.repositories.item import ItemRepository
from app.schemas.item import ItemCreate, ItemUpdate


class ItemService:
    def __init__(self, repository: ItemRepository) -> None:
        self._repository = repository

    async def create_item(self, data: ItemCreate) -> Item:
        item = Item(**data.model_dump())
        return await self._repository.create(item)

    async def get_item(self, item_id: int) -> Item:
        item = await self._repository.get(item_id)
        if item is None:
            raise ItemNotFoundError(item_id)
        return item

    async def list_items(self, *, limit: int = 20, offset: int = 0) -> list[Item]:
        return await self._repository.list(limit=limit, offset=offset)

    async def update_item(self, item_id: int, data: ItemUpdate) -> Item:
        item = await self.get_item(item_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        return item

    async def delete_item(self, item_id: int) -> None:
        item = await self.get_item(item_id)
        await self._repository.delete(item)
