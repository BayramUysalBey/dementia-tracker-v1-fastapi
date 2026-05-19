import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_create_and_read_note(
    client: AsyncClient, 
    user_mock_data: dict, 
    note_mock_data: dict
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
    
    # 3. Create a note 
    note_mock_data["user_id"] = created_user_id 
    response_note = await client.post(
        "/api/v1/note", 
        json=note_mock_data,
        headers=auth_headers
    )
    assert response_note.status_code == 201
    created_note = response_note.json()
    assert created_note["category"] == note_mock_data["category"]
    assert created_note["type"] == note_mock_data["type"]
    assert "id" in created_note
    assert "user_id" in created_note
    
    # 4. Read note
    response_read = await client.get("/api/v1/note", headers=auth_headers)
    assert response_read.status_code == 200
    note_list = response_read.json()
    assert len(note_list) == 1
    assert note_list[0]["id"] == created_note["id"]
    
@pytest.mark.asyncio
async def test_update_note(client: AsyncClient, user_mock_data: dict, note_mock_data: dict):
    response_create = await client.post("/api/v1/users/create", json=user_mock_data)
    created_user_id = response_create.json()["id"]
    login_data = {"username": user_mock_data["email"], "password": user_mock_data["password"]}
    response_login = await client.post("/api/v1/auth/token", data=login_data)
    token = response_login.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    note_mock_data["user_id"] = created_user_id
    create_response = await client.post("/api/v1/note", json=note_mock_data, headers=auth_headers)
    note_id = create_response.json()["id"]
    update_data = {
        "title": "Updated Meeting Notes",
        "content": "The patient is doing much better today."
    }
    response = await client.patch(f"/api/v1/note/{note_id}", json=update_data, headers=auth_headers)
    
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Meeting Notes"
    assert response.json()["content"] == "The patient is doing much better today."

    

@pytest.mark.asyncio  
async def test_create_note_unauthorized(client: AsyncClient, note_mock_data: dict):
    response = await client.post("/api/v1/note", json=note_mock_data)
    assert response.status_code == 401
    error_response = response.json()
    assert error_response["detail"] == "Not authenticated"