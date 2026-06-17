import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_and_read_note(
    client: AsyncClient,
    note_mock_data: dict
):
    # 1. Create a caregiver
    caregiver_data = {
        "first_name": "Care", "last_name": "Giver", "role": "caregiver",
        "email": "caregiver_note@example.com", "password": "securepassword123"
    }
    await client.post("/api/v1/users/create", json=caregiver_data)

    # 2. Create a patient
    patient_data = {
        "first_name": "Pat", "last_name": "Ient", "role": "patient",
        "email": "patient_note@example.com", "password": "securepassword123"
    }
    patient_resp = await client.post("/api/v1/users/create", json=patient_data)
    patient_id = patient_resp.json()["id"]

    # 3. Login as caregiver
    login = await client.post("/api/v1/auth/token",
        data={"username": caregiver_data["email"], "password": caregiver_data["password"]})
    token = login.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 4. Assign the patient to the caregiver
    await client.post("/api/v1/care-assignments",
        json={"patient_id": patient_id}, headers=auth_headers)

    # 5. Create a note about the patient
    note_mock_data["user_id"] = patient_id
    response_note = await client.post("/api/v1/note", json=note_mock_data, headers=auth_headers)
    assert response_note.status_code == 201
    created_note = response_note.json()
    assert created_note["category"] == note_mock_data["category"]
    assert "id" in created_note

    # 6. Read notes
    response_read = await client.get("/api/v1/note", headers=auth_headers)
    assert response_read.status_code == 200
    assert len(response_read.json()) == 1
    
@pytest.mark.asyncio
async def test_update_note(client: AsyncClient, note_mock_data: dict):
    # 1. Create a caregiver
    caregiver_data = {
        "first_name": "Care", "last_name": "Giver", "role": "caregiver",
        "email": "caregiver_update_note@example.com", "password": "securepassword123"
    }
    await client.post("/api/v1/users/create", json=caregiver_data)

    # 2. Create a patient
    patient_data = {
        "first_name": "Pat", "last_name": "Ient", "role": "patient",
        "email": "patient_update_note@example.com", "password": "securepassword123"
    }
    patient_resp = await client.post("/api/v1/users/create", json=patient_data)
    patient_id = patient_resp.json()["id"]

    # 3. Login as caregiver
    login_data = {"username": caregiver_data["email"], "password": caregiver_data["password"]}
    response_login = await client.post("/api/v1/auth/token", data=login_data)
    token = response_login.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 4. Assign the patient to the caregiver
    await client.post("/api/v1/care-assignments",
        json={"patient_id": patient_id}, headers=auth_headers)

    # 5. Create a note about the patient
    note_mock_data["user_id"] = patient_id
    create_response = await client.post("/api/v1/note", json=note_mock_data, headers=auth_headers)
    assert create_response.status_code == 201
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
    

@pytest.mark.asyncio  
async def test_create_note_invalid_title(
    client: AsyncClient, 
    user_mock_data: dict, 
    note_mock_data: dict
):
    response_create = await client.post("/api/v1/users/create", json=user_mock_data)
    login_data = {
        "username": user_mock_data["email"],
        "password": user_mock_data["password"]
    }
    response_login = await client.post("/api/v1/auth/token", data=login_data)
    token = response_login.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    bad_data = note_mock_data.copy()
    bad_data["title"] = 777
    bad_data["user_id"] = response_create.json()["id"]

    response = await client.post(
        "/api/v1/note", 
        json=bad_data,
        headers=auth_headers
    )
    assert response.status_code == 422
    error_response = response.json()
    assert error_response["detail"][0]["loc"] == ["body", "title"]