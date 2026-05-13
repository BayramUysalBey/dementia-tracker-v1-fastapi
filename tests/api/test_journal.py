import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_create_and_read_journal(
    client: AsyncClient, 
    user_mock_data: dict, 
    journal_mock_data: dict
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
    
    # 3. Create an journal
    journal_mock_data["user_id"] = created_user_id 
    
    response_journal = await client.post(
        "/api/v1/journal", 
        json=journal_mock_data,
        headers=auth_headers
    )
    assert response_journal.status_code == 201
    created_journal = response_journal.json()
    assert created_journal["user_diary_entry"] == journal_mock_data["user_diary_entry"]
    assert created_journal["author_diary_entry"] == journal_mock_data["author_diary_entry"]
    assert "id" in created_journal
    assert "user_id" in created_journal
    
    # 4. Read journals
    response_read = await client.get("/api/v1/journal", headers=auth_headers)
    assert response_read.status_code == 200
    journals_list = response_read.json()
    assert len(journals_list) == 1
    assert journals_list[0]["id"] == created_journal["id"]
    

@pytest.mark.asyncio  
async def test_create_journal_unauthorized(client: AsyncClient, journal_mock_data: dict):
    journal_mock_data["user_id"] = str(uuid.uuid4())
    response = await client.post("/api/v1/journal", json=journal_mock_data)
    assert response.status_code == 401
    error_response = response.json()
    assert error_response["detail"] == "Not authenticated"