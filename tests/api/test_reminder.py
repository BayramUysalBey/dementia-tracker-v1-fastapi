import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_create_and_read_reminder(
    client: AsyncClient, 
    user_mock_data: dict, 
    reminder_mock_data: dict
):
    # 1. Create a user
    response_create = await client.post("/api/v1/users/create", json=user_mock_data)
    assert response_create.status_code == 201
    created_user_id = response_create.json()["id"]
    
    # 2. Login to get token
    login_data = {
        "username": user_mock_data["email"],
        "password": user_mock_data["password"]
    }
    response_login = await client.post("/api/v1/auth/token", data=login_data)
    assert response_login.status_code == 200
    token = response_login.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Create an reminder    
    response_reminder = await client.post(
        "/api/v1/reminder", 
        json=reminder_mock_data,
        headers=auth_headers
    )
    assert response_reminder.status_code == 201
    created_reminder = response_reminder.json()
    assert created_reminder["related_entity_type"] == reminder_mock_data["related_entity_type"]
    assert created_reminder["name"] == reminder_mock_data["name"]
    assert "id" in created_reminder
    assert "user_id" in created_reminder
    
    # 4. Read reminder
    response_read = await client.get("/api/v1/reminder", headers=auth_headers)
    assert response_read.status_code == 200
    reminder_list = response_read.json()
    assert len(reminder_list) == 1
    assert reminder_list[0]["id"] == created_reminder["id"]
    

@pytest.mark.asyncio  
async def test_create_reminder_unauthorized(client: AsyncClient, reminder_mock_data: dict):
    reminder_mock_data["user_id"] = str(uuid.uuid4())
    response = await client.post("/api/v1/reminder", json=reminder_mock_data)
    assert response.status_code == 401
    error_response = response.json()
    assert error_response["detail"] == "Not authenticated"
    

@pytest.mark.asyncio  
async def test_create_reminder_invalid_related_entity_id(
    client: AsyncClient, 
    user_mock_data: dict, 
    reminder_mock_data: dict
):
    response_create = await client.post("/api/v1/users/create", json=user_mock_data)
    login_data = {
        "username": user_mock_data["email"],
        "password": user_mock_data["password"]
    }
    response_login = await client.post("/api/v1/auth/token", data=login_data)
    token = response_login.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    bad_data = reminder_mock_data.copy()
    bad_data["related_entity_id"] = 789
    bad_data["user_id"] = response_create.json()["id"]

    response = await client.post(
        "/api/v1/reminder", 
        json=bad_data,
        headers=auth_headers
    )
    assert response.status_code == 422
    error_response = response.json()
    
    # print("\n--- API ERROR RESPONSE ---")
    # print(error_response)
    # print("--------------------------\n")
    
    assert error_response["detail"][0]["loc"] == ["body", "related_entity_id"]