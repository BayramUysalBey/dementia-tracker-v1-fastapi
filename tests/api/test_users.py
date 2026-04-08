import pytest
from httpx import AsyncClient
from app.schemas.users import UserRead

@pytest.mark.asyncio
async def test_user_mock_data(client: AsyncClient, user_mock_data: dict):
    
    response_create = await client.post("/api/v1/users/create", json=user_mock_data)
    assert response_create.status_code == 201
    
    user_data = response_create.json()
    user_id = user_data["id"]
    
    auth_headers = {"Secret-User-Id": user_id}
    
    response_read = await client.get("/api/v1/users/me", headers=auth_headers)
    assert response_read.status_code == 200
    assert response_read.json()["email"] == "simple@example.com"
    # Pydantic Schema Validation
    validated_data = UserRead(**response_read.json())
    assert validated_data.email == "simple@example.com"

    update_payload = {"username": "updated_simple_username"}
    
    response_update = await client.patch("/api/v1/users/me", headers=auth_headers, json=update_payload)
    assert response_update.status_code == 200
    assert response_update.json()["username"] == "updated_simple_username"