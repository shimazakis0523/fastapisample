from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import ItemServiceDep
from app.core.auth import require_permission, verify_token
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate

ResponsesSpec = dict[int | str, dict[str, Any]]

_UNAUTHORIZED_RESPONSE: ResponsesSpec = {401: {"description": "Missing or invalid access token"}}
_FORBIDDEN_RESPONSE: ResponsesSpec = {403: {"description": "Missing required permission"}}

router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(verify_token)],
    responses=_UNAUTHORIZED_RESPONSE,
)

_NOT_FOUND_RESPONSE: ResponsesSpec = {404: {"description": "Item not found"}}
# Starlette rejects a syntactically invalid JSON body itself, before FastAPI's
# usual 422 validation ever runs, so any body-accepting endpoint can also return
# this.
_MALFORMED_BODY_RESPONSE: ResponsesSpec = {400: {"description": "Malformed request body"}}

# Bounded to a signed 32-bit range: matches the database column width and keeps
# out-of-range input a 422 instead of an unhandled overflow from the DB driver.
_INT32_MAX = 2_147_483_647
ItemId = Annotated[int, Path(ge=1, le=_INT32_MAX)]


@router.post(
    "",
    response_model=ItemRead,
    status_code=status.HTTP_201_CREATED,
    responses=_MALFORMED_BODY_RESPONSE,
)
async def create_item(data: ItemCreate, service: ItemServiceDep) -> ItemRead:
    item = await service.create_item(data)
    return ItemRead.model_validate(item)


@router.get("", response_model=list[ItemRead])
async def list_items(
    service: ItemServiceDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0, le=_INT32_MAX)] = 0,
) -> list[ItemRead]:
    items = await service.list_items(limit=limit, offset=offset)
    return [ItemRead.model_validate(item) for item in items]


@router.get("/{item_id}", response_model=ItemRead, responses=_NOT_FOUND_RESPONSE)
async def get_item(item_id: ItemId, service: ItemServiceDep) -> ItemRead:
    item = await service.get_item(item_id)
    return ItemRead.model_validate(item)


@router.patch(
    "/{item_id}",
    response_model=ItemRead,
    responses={**_NOT_FOUND_RESPONSE, **_MALFORMED_BODY_RESPONSE},
)
async def update_item(item_id: ItemId, data: ItemUpdate, service: ItemServiceDep) -> ItemRead:
    item = await service.update_item(item_id, data)
    return ItemRead.model_validate(item)


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("delete:items"))],
    responses={**_NOT_FOUND_RESPONSE, **_FORBIDDEN_RESPONSE},
)
async def delete_item(item_id: ItemId, service: ItemServiceDep) -> None:
    await service.delete_item(item_id)
