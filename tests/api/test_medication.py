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
	assert created_medication["medication_name"] == "Testamine"
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

@pytest.mark.asyncio
async def test_read_medication(client: AsyncClient, user_mock_data: dict, medication_mock_data: dict):
	await client.post("api/v1/users/create", json=user_mock_data)
	login_data = {"username": user_mock_data["email"], "password": user_mock_data["password"]}
	response_login = await client.post("api/v1/auth/token", data=login_data)
	token = response_login.json()["access_token"]
	auth_headers = {"Authorization": f"Bearer {token}"}

	await client.post("api/v1/medication", json=medication_mock_data, headers=auth_headers)
	response = await client.get("api/v1/medication", headers=auth_headers)
	assert response.status_code == 200
	medication_list = response.json()
	assert len(medication_list) == 1
	assert medication_list[0]["medication_name"] == "Testamine"

@pytest.mark.asyncio
async def test_update_medication(client: AsyncClient, user_mock_data: dict, medication_mock_data: dict):
	await client.post("api/v1/users/create", json=user_mock_data)
	login_data = {"username": user_mock_data["email"], "password": user_mock_data["password"]}
	response_login = await client.post("api/v1/auth/token", data=login_data)
	token = response_login.json()["access_token"]
	auth_headers = {"Authorization": f"Bearer {token}"}
	create_response = await client.post("api/v1/medication", json=medication_mock_data, headers=auth_headers)
	medication_id = create_response.json()["id"]
	update_data = {"dosage": "20 mg"}
	response = await client.patch(f"api/v1/medication/{medication_id}", json=update_data, headers=auth_headers)
	assert response.status_code == 200
	assert response.json()["dosage"] == "20 mg"

@pytest.mark.asyncio
async def test_medication_defaults_to_active(
    client: AsyncClient,
    user_mock_data: dict,
    medication_mock_data: dict
):
    await client.post("/api/v1/users/create", json=user_mock_data)
    login_data = {
        "username": user_mock_data["email"],
        "password": user_mock_data["password"]
    }
    response_login = await client.post("/api/v1/auth/token", data=login_data)
    token = response_login.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/medication", json=medication_mock_data, headers=auth_headers
    )
    assert response.status_code == 201
    # a newly created medication is active without the client sending a status
    assert response.json()["status"] == "active"

@pytest.mark.asyncio
async def test_discontinue_medication_keeps_record(
    client: AsyncClient,
    user_mock_data: dict,
    medication_mock_data: dict
):
    await client.post("/api/v1/users/create", json=user_mock_data)
    login_data = {
        "username": user_mock_data["email"],
        "password": user_mock_data["password"]
    }
    response_login = await client.post("/api/v1/auth/token", data=login_data)
    token = response_login.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    create_response = await client.post(
        "/api/v1/medication", json=medication_mock_data, headers=auth_headers
    )
    medication_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/v1/medication/{medication_id}",
        json={"status": "discontinued"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "discontinued"

    # the record is retired, not removed — it is still readable
    read_response = await client.get("/api/v1/medication", headers=auth_headers)
    assert read_response.status_code == 200
    medication_list = read_response.json()
    assert len(medication_list) == 1
    assert medication_list[0]["id"] == medication_id
    assert medication_list[0]["status"] == "discontinued"
