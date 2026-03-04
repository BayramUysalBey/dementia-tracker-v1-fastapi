from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_message():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Dementia Tracker V1 API"}

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "up"

def test_get_items_list():
    response = client.get("/items")
    assert response.status_code == 200
    assert len(response.json()) >= 3

def test_get_item_id_success():
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Memory Aid"

def test_get_item_id_not_found():
    response = client.get("/items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

def test_create_item_success():
    new_item = {
        "name": "New Tracker",
        "price": 50.0,
        "is_offer": False,
        "user_id": 1,
        "category": "Safety"
    }
    response = client.post("/items", json=new_item)
    assert response.status_code == 201
    assert response.json()["name"] == "New Tracker"

def test_delete_item_success():
    new_item = {
        "name": "To Delete",
        "price": 10.0,
        "is_offer": False,
        "user_id": 1,
        "category": "Test"
    }
    create_res = client.post("/items", json=new_item)
    item_id = create_res.json()["id"]
    
    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 204

def test_delete_item_not_found():
    response = client.delete("/items/999")
    assert response.status_code == 404

def test_user_filtering():
    response = client.get("/users/1/items?category=Safety")
    assert response.status_code == 200
    items = response.json()
    assert all(i["user_id"] == 1 and i["category"] == "Safety" for i in items)
