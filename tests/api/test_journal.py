import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_create_and_read_journal(
    client: AsyncClient,
    journal_mock_data: dict
):
    # 1. Create a caregiver
    caregiver_data = {
        "first_name": "Care", "last_name": "Giver", "role": "caregiver",
        "email": "caregiver_journal@example.com", "password": "securepassword123"
    }
    await client.post("/api/v1/users/create", json=caregiver_data)

    # 2. Create a patient
    patient_data = {
        "first_name": "Pat", "last_name": "Ient", "role": "patient",
        "email": "patient_journal@example.com", "password": "securepassword123"
    }
    patient_resp = await client.post("/api/v1/users/create", json=patient_data)
    assert patient_resp.status_code == 201
    patient_id = patient_resp.json()["id"]

    # 3. Login as caregiver
    login_data = {
        "username": caregiver_data["email"],
        "password": caregiver_data["password"]
    }
    response_login = await client.post("/api/v1/auth/token", data=login_data)
    assert response_login.status_code == 200
    token = response_login.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 4. Assign the patient to the caregiver
    await client.post("/api/v1/care-assignments",
        json={"patient_id": patient_id}, headers=auth_headers)

    # 5. Create a journal about the patient
    journal_mock_data["user_id"] = patient_id

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