import pytest
from httpx import AsyncClient


# Integration Test
@pytest.mark.asyncio
async def test_user_mock_data(client: AsyncClient, user_mock_data: dict):
    
    response_create = await client.post("/api/v1/users/create", json=user_mock_data)
    assert response_create.status_code == 201
    
    login_data = {
        "username": user_mock_data["email"],
        "password": user_mock_data["password"]
    }
    
    response_login = await client.post("/api/v1/auth/token", data=login_data)
    assert response_login.status_code == 200
    real_token = response_login.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {real_token}"}
    
    response_read = await client.get("/api/v1/users/me", headers=auth_headers)
    assert response_read.status_code == 200
    assert response_read.json()["email"] == user_mock_data["email"]
	
    update_payload = {"username": "updated_simple_username"}
    response_update = await client.patch("/api/v1/users/me", headers=auth_headers, json=update_payload)
    assert response_update.status_code == 200
    assert response_update.json()["username"] == "updated_simple_username"
    

# Unit Test
@pytest.mark.asyncio
async def test_get_user_data(authenticated_client): 
    response = await authenticated_client.get("/api/v1/users/me")
    assert response.status_code == 200 
    assert response.json()["username"] == "testuser"
    

@pytest.mark.asyncio  
async def test_create_user_invalid_email(client: AsyncClient):
    bad_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "not-an-email",
        "password": "securepassword123"
    }
    response = await client.post("/api/v1/users/create", json=bad_data)
    assert response.status_code == 422 


    

