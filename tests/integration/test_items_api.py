from httpx import AsyncClient


async def test_create_item(client: AsyncClient) -> None:
    response = await client.post("/api/v1/items", json={"name": "Widget", "price": 9.99})

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Widget"
    assert body["id"] is not None


async def test_get_item_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/items/999")

    assert response.status_code == 404


async def test_list_and_update_and_delete_item(client: AsyncClient) -> None:
    create_response = await client.post("/api/v1/items", json={"name": "Gadget", "price": 5})
    item_id = create_response.json()["id"]

    list_response = await client.get("/api/v1/items")
    assert list_response.status_code == 200
    assert any(item["id"] == item_id for item in list_response.json())

    update_response = await client.patch(f"/api/v1/items/{item_id}", json={"price": 7.5})
    assert update_response.status_code == 200
    assert update_response.json()["price"] == 7.5

    delete_response = await client.delete(f"/api/v1/items/{item_id}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/api/v1/items/{item_id}")
    assert get_response.status_code == 404


async def test_create_item_validation_error(client: AsyncClient) -> None:
    response = await client.post("/api/v1/items", json={"name": "", "price": -1})

    assert response.status_code == 422
