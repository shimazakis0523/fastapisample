import pytest

from app.core.exceptions import ItemNotFoundError
from app.schemas.item import ItemCreate, ItemUpdate
from app.services.item import ItemService


async def test_create_and_get_item(item_service: ItemService) -> None:
    created = await item_service.create_item(ItemCreate(name="Widget", price=9.99))

    fetched = await item_service.get_item(created.id)

    assert fetched.id == created.id
    assert fetched.name == "Widget"


async def test_get_missing_item_raises(item_service: ItemService) -> None:
    with pytest.raises(ItemNotFoundError):
        await item_service.get_item(999)


async def test_update_item(item_service: ItemService) -> None:
    created = await item_service.create_item(ItemCreate(name="Widget", price=9.99))

    updated = await item_service.update_item(created.id, ItemUpdate(price=12.5))

    assert updated.price == 12.5
    assert updated.name == "Widget"


async def test_delete_item(item_service: ItemService) -> None:
    created = await item_service.create_item(ItemCreate(name="Widget", price=9.99))

    await item_service.delete_item(created.id)

    with pytest.raises(ItemNotFoundError):
        await item_service.get_item(created.id)


async def test_list_items(item_service: ItemService) -> None:
    await item_service.create_item(ItemCreate(name="A", price=1))
    await item_service.create_item(ItemCreate(name="B", price=2))

    items = await item_service.list_items(limit=10, offset=0)

    assert len(items) == 2
