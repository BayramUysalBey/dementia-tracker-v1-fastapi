import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_read_habit(
    client: AsyncClient, 
    user_mock_data: dict, 
    habit_mock_data: dict
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
    
    # 3. Create a habit   
    response_habit = await client.post(
        "/api/v1/habit", 
        json=habit_mock_data,
        headers=auth_headers
    )
    assert response_habit.status_code == 201
    created_habit = response_habit.json()
    assert created_habit["target_frequency"] == habit_mock_data["target_frequency"]
    assert created_habit["name"] == habit_mock_data["name"]
    assert "id" in created_habit
    assert "user_id" in created_habit
    
    # 4. Read habit
    response_read = await client.get("/api/v1/habit", headers=auth_headers)
    assert response_read.status_code == 200
    habit_list = response_read.json()
    assert len(habit_list) == 1
    assert habit_list[0]["id"] == created_habit["id"]
    
@pytest.mark.asyncio
async def test_update_habit(client: AsyncClient, user_mock_data: dict, habit_mock_data: dict):
	await client.post("/api/v1/users/create", json=user_mock_data)
	login_data = {"username": user_mock_data["email"], "password": user_mock_data["password"]}
	response_login = await client.post("/api/v1/auth/token", data=login_data)
	token = response_login.json()["access_token"]
	auth_headers = {"Authorization": f"Bearer {token}"}    
	create_response = await client.post("/api/v1/habit", json=habit_mock_data, headers=auth_headers)
	habit_id = create_response.json()["id"]
	update_data = {"streak_count": 4}
	response = await client.patch(f"/api/v1/habit/{habit_id}", json=update_data, headers=auth_headers)
	assert response.status_code == 200
	assert response.json()["streak_count"] == 4
    

@pytest.mark.asyncio  
async def test_create_habit_unauthorized(client: AsyncClient, habit_mock_data: dict):
    response = await client.post("/api/v1/habit", json=habit_mock_data)
    assert response.status_code == 401
    error_response = response.json()
    assert error_response["detail"] == "Not authenticated"