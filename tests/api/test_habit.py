import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_read_habit(
    client: AsyncClient, 
    caregiver_with_patient: dict, 
    habit_mock_data: dict
):
    auth_headers = caregiver_with_patient["auth_headers"]
    patient_id = caregiver_with_patient["patient_id"]

    # Create a habit   
    habit_data = {**habit_mock_data, "user_id": patient_id}
    response_habit = await client.post(
        "/api/v1/habit",
        json=habit_data,
        headers=auth_headers
    )
    assert response_habit.status_code == 201
    created_habit = response_habit.json()
    assert created_habit["target_frequency"] == habit_mock_data["target_frequency"]
    assert created_habit["name"] == habit_mock_data["name"]
    assert "id" in created_habit
    assert created_habit["user_id"] == patient_id
    
    # Read habit
    response_read = await client.get("/api/v1/habit", headers=auth_headers)
    assert response_read.status_code == 200
    habit_list = response_read.json()
    assert len(habit_list) == 1
    assert habit_list[0]["id"] == created_habit["id"]


@pytest.mark.asyncio
async def test_update_habit(client: AsyncClient, caregiver_with_patient: dict, habit_mock_data: dict):
    auth_headers = caregiver_with_patient["auth_headers"]
    patient_id = caregiver_with_patient["patient_id"]
    habit_data = {**habit_mock_data, "user_id": patient_id}
    create_response = await client.post("/api/v1/habit", json=habit_data, headers=auth_headers)
    assert create_response.status_code == 201
    habit_id = create_response.json()["id"]
    update_data = {"target_frequency": "Twice daily"}
    response = await client.patch(f"/api/v1/habit/{habit_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["target_frequency"] == "Twice daily"
    

@pytest.mark.asyncio  
async def test_create_habit_unauthorized(client: AsyncClient, habit_mock_data: dict):
    response = await client.post("/api/v1/habit", json=habit_mock_data)
    assert response.status_code == 401
    error_response = response.json()
    assert error_response["detail"] == "Not authenticated"

@pytest.mark.asyncio
async def test_habit_defaults_to_active(
    client: AsyncClient,
    caregiver_with_patient: dict,
    habit_mock_data: dict
):
    auth_headers = caregiver_with_patient["auth_headers"]
    patient_id = caregiver_with_patient["patient_id"]
    habit_data = {**habit_mock_data, "user_id": patient_id}
    response = await client.post(
        "/api/v1/habit", json=habit_data, headers=auth_headers
    )
    assert response.status_code == 201
    # a newly created habit is active without the client sending a status
    assert response.json()["status"] == "active"


@pytest.mark.asyncio
async def test_discontinue_habit_keeps_record(
    client: AsyncClient,
    caregiver_with_patient: dict,
    habit_mock_data: dict
):
    auth_headers = caregiver_with_patient["auth_headers"]
    patient_id = caregiver_with_patient["patient_id"]
    habit_data = {**habit_mock_data, "user_id": patient_id}

    create_response = await client.post(
        "/api/v1/habit", json=habit_data, headers=auth_headers
    )
    assert create_response.status_code == 201
    habit_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/v1/habit/{habit_id}",
        json={"status": "discontinued"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "discontinued"

    # the record is retired, not removed — it is still readable
    read_response = await client.get("/api/v1/habit", headers=auth_headers)
    assert read_response.status_code == 200
    habit_list = read_response.json()
    assert len(habit_list) == 1
    assert habit_list[0]["id"] == habit_id
    assert habit_list[0]["status"] == "discontinued"



@pytest.mark.asyncio
async def test_cannot_set_streak_count_via_update(
    client: AsyncClient,
    caregiver_with_patient: dict,
    habit_mock_data: dict
):
    auth_headers = caregiver_with_patient["auth_headers"]
    patient_id = caregiver_with_patient["patient_id"]
    habit_data = {**habit_mock_data, "user_id": patient_id}
    create_response = await client.post(
        "/api/v1/habit", json=habit_data, headers=auth_headers
    )
    assert create_response.status_code == 201
    habit_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/v1/habit/{habit_id}",
        json={"streak_count": 4},
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "streak_count"]


@pytest.mark.asyncio
async def test_cannot_create_habit_for_unassigned_patient(
    client: AsyncClient,
    habit_mock_data: dict
):
    # 1. A caregiver registers
    caregiver_data = {
        "first_name": "Care", "last_name": "Giver", "role": "caregiver",
        "email": "unassigned_caregiver_habit@example.com", "password": "securepassword123"
    }
    await client.post("/api/v1/users/create", json=caregiver_data)

    # 2. An unrelated patient registers
    patient_data = {
        "first_name": "Pat", "last_name": "Ient", "role": "patient",
        "email": "unassigned_patient_habit@example.com", "password": "securepassword123"
    }
    patient_resp = await client.post("/api/v1/users/create", json=patient_data)
    assert patient_resp.status_code == 201
    patient_id = patient_resp.json()["id"]

    # 3. The caregiver logs in
    login_data = {
        "username": caregiver_data["email"],
        "password": caregiver_data["password"]
    }
    response_login = await client.post("/api/v1/auth/token", data=login_data)
    assert response_login.status_code == 200
    token = response_login.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 4. No care assignment is created — the caregiver writes anyway
    habit_mock_data["user_id"] = patient_id
    response = await client.post(
        "/api/v1/habit",
        json=habit_mock_data,
        headers=auth_headers
    )

    # 5. verify_caregiver_access must refuse
    assert response.status_code == 403
    assert response.json()["detail"] == "You are not assigned to this patient"


@pytest.mark.asyncio
async def test_cannot_create_habit_about_self(
    client: AsyncClient,
    habit_mock_data: dict
):
    # 1. A caregiver registers — keep the id from the response
    caregiver_data = {
        "first_name": "Care", "last_name": "Giver", "role": "caregiver",
        "email": "self_author_habit@example.com", "password": "securepassword123"
    }
    response_create = await client.post("/api/v1/users/create", json=caregiver_data)
    assert response_create.status_code == 201
    caregiver_id = response_create.json()["id"]

    # 2. They log in
    login_data = {
        "username": caregiver_data["email"],
        "password": caregiver_data["password"]
    }
    response_login = await client.post("/api/v1/auth/token", data=login_data)
    assert response_login.status_code == 200
    token = response_login.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 3. They try to write a habit about THEMSELVES
    habit_mock_data["user_id"] = caregiver_id
    response = await client.post(
        "/api/v1/habit",
        json=habit_mock_data,
        headers=auth_headers
    )

    # 4. The self-authoring guard must refuse
    assert response.status_code == 403
    assert response.json()["detail"] == "Records must be authored by a caregiver, not by the patient"

@pytest.mark.asyncio
async def test_cannot_update_habit_if_not_author(
    client: AsyncClient,
    caregiver_with_patient: dict,
    habit_mock_data: dict
):
    # 1. The assigned caregiver (author) creates the habit
    auth_headers_author = caregiver_with_patient["auth_headers"]
    patient_id = caregiver_with_patient["patient_id"]
    habit_data = {**habit_mock_data, "user_id": patient_id}

    create_response = await client.post(
        "/api/v1/habit", json=habit_data, headers=auth_headers_author
    )
    assert create_response.status_code == 201
    habit_id = create_response.json()["id"]

    # 2. A second caregiver registers
    other_caregiver_data = {
        "first_name": "Another", "last_name": "Caregiver", "role": "caregiver",
        "email": "not_the_author_habit@example.com", "password": "securepassword123"
    }
    other_response = await client.post("/api/v1/users/create", json=other_caregiver_data)
    assert other_response.status_code == 201

    # 3. The second caregiver logs in and is assigned to the same patient,
    #    so the ONLY difference between the two caregivers is authorship
    login_data = {
        "username": other_caregiver_data["email"],
        "password": other_caregiver_data["password"]
    }
    response_login = await client.post("/api/v1/auth/token", data=login_data)
    assert response_login.status_code == 200
    other_token = response_login.json()["access_token"]
    auth_headers_other = {"Authorization": f"Bearer {other_token}"}

    assign_response = await client.post(
        "/api/v1/care-assignments",
        json={"patient_id": patient_id},
        headers=auth_headers_other,
    )
    assert assign_response.status_code == 201

    # 4. The second caregiver tries to update the habit they didn't author
    response = await client.patch(
        f"/api/v1/habit/{habit_id}",
        json={"target_frequency": "Never"},
        headers=auth_headers_other,
    )

    # 5. The server refuses (404: it doesn't confirm the record exists)
    assert response.status_code == 404
    assert response.json()["detail"] == "Habit not found"

    # 6. The data is unchanged: read as the author, the value is still the original
    read_response = await client.get("/api/v1/habit", headers=auth_headers_author)
    assert read_response.status_code == 200
    assert read_response.json()[0]["target_frequency"] == "Daily"