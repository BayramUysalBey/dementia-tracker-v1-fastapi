import pytest
from httpx import AsyncClient
from app.main import app




@pytest.mark.asyncio
async def test_root_message(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Dementia Tracker V1 API"}

@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "connected"

@pytest.mark.asyncio
async def test_get_items_list(client: AsyncClient):
    response = await client.get("/items")
    assert response.status_code == 200
    assert len(response.json()) >= 3

@pytest.mark.asyncio
async def test_get_item_id_success(client: AsyncClient):
    response = await client.get("/items/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Memory Aid"

@pytest.mark.asyncio
async def test_get_item_id_not_found(client: AsyncClient):
    response = await client.get("/items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

@pytest.mark.asyncio
async def test_create_item_success(client: AsyncClient):
    new_item = {
        "name": "New Tracker",
        "price": 50.0,
        "is_offer": False,
        "user_id": 1,
        "category": "Safety"
    }
    response = await client.post("/items", json=new_item)
    assert response.status_code == 201
    assert response.json()["name"] == "New Tracker"

@pytest.mark.asyncio
async def test_delete_item_success(client: AsyncClient):
    new_item = {
        "name": "To Delete",
        "price": 10.0,
        "is_offer": False,
        "user_id": 1,
        "category": "Test"
    }
    create_res = await client.post("/items", json=new_item)
    item_id = create_res.json()["id"]
    
    response =await  client.delete(f"/items/{item_id}")
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_delete_item_not_found(client: AsyncClient):
    response = await client.delete("/items/999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_user_filtering(client: AsyncClient):
    response = await client.get("/users/1/items?category=Safety")
    assert response.status_code == 200
    items = response.json()
    assert all(i["user_id"] == 1 and i["category"] == "Safety" for i in items)
