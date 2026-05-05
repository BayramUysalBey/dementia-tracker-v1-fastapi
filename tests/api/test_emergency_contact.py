import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_and_read_emergency_contact(
    client: AsyncClient, 
    user_mock_data: dict, 
    emergency_contact_mock_data: dict
):
    # 1. Create a user
    response_create = await client.post("/api/v1/users/create", json=user_mock_data)
    assert response_create.status_code == 201
    
    # 2. Login to get token
    login_data = {
        "username": user_mock_data["email"],
        "password": user_mock_data["password"]
    }
    response_login = await client.post("/api/v1/auth/token", data=login_data)
    assert response_login.status_code == 200
    token = response_login.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Create an emergency contact
    response_contact = await client.post(
        "/api/v1/emergency_contact", 
        json=emergency_contact_mock_data,
        headers=auth_headers
    )
    assert response_contact.status_code == 201
    created_contact = response_contact.json()
    assert created_contact["first_name"] == emergency_contact_mock_data["first_name"]
    assert created_contact["email"] == emergency_contact_mock_data["email"]
    assert "id" in created_contact
    assert "user_id" in created_contact
    
    # 4. Read emergency contacts
    response_read = await client.get("/api/v1/emergency_contact", headers=auth_headers)
    assert response_read.status_code == 200
    contacts_list = response_read.json()
    assert len(contacts_list) == 1
    assert contacts_list[0]["id"] == created_contact["id"]
