import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_medication(client: AsyncClient, user_mock_data: dict, medication_mock_data: dict):
	await client.post("api/v1/users/create", json=user_mock_data)
	login_data = {"username": user_mock_data["email"], "password": user_mock_data["password"]}
	response_login = await client.post("api/v1/auth/token", data=login_data)
	token = response_login.json()["access_token"]
	auth_headers = {"Authorization": f"Bearer {token}"}

	response = await client.post("api/v1/medication", json=medication_mock_data, headers=auth_headers)
	assert response.status_code == 201
	created_medication = response.json()
	assert created_medication["medication_name"] == "Ebixa"
	assert created_medication["dosage"] == "10 mg"
	assert "id" in created_medication
	assert "user_id" in created_medication

@pytest.mark.asyncio
async def test_dosage_medication(client: AsyncClient, user_mock_data: dict, medication_mock_data: dict):
	await client.post("api/v1/users/create", json=user_mock_data)
	login_data = {"username": user_mock_data["email"], "password": user_mock_data["password"]}
	response_login = await client.post("api/v1/auth/token", data=login_data)
	token = response_login.json()["access_token"]
	auth_headers = {"Authorization": f"Bearer {token}"}

	bad_data = medication_mock_data.copy()
	bad_data["dosage"] = "10 miligrams"
	
	response = await client.post("api/v1/medication", json=bad_data, headers=auth_headers)
	assert response.status_code == 422
	error_response = response.json()
	assert error_response["detail"][0]["loc"] == ["body", "dosage"]