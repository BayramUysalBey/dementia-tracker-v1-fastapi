import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_medication(client: AsyncClient, caregiver_with_patient: dict, medication_mock_data: dict):
    auth_headers = caregiver_with_patient["auth_headers"]
    patient_id = caregiver_with_patient["patient_id"]
    caregiver_id = caregiver_with_patient["caregiver_id"]
    medication_data = {**medication_mock_data, "user_id": patient_id}

    response = await client.post("/api/v1/medication", json=medication_data, headers=auth_headers)
    assert response.status_code == 201
    created_medication = response.json()
    assert created_medication["medication_name"] == "Testamine"
    assert created_medication["dosage"] == "10 mg"
    # About the patient, written by the caregiver (author comes from the token)
    assert created_medication["user_id"] == patient_id
    assert created_medication["author_id"] == caregiver_id
 
@pytest.mark.asyncio
async def test_dosage_medication(client: AsyncClient, caregiver_with_patient: dict, medication_mock_data: dict):
    auth_headers = caregiver_with_patient["auth_headers"]
    patient_id = caregiver_with_patient["patient_id"]
    bad_data = {**medication_mock_data, "user_id": patient_id, "dosage": "10 miligrams"}
    response = await client.post("/api/v1/medication", json=bad_data, headers=auth_headers)
    assert response.status_code == 422
    error_response = response.json()
    assert len(error_response["detail"]) == 1
    assert error_response["detail"][0]["loc"] == ["body", "dosage"]

@pytest.mark.asyncio
async def test_read_medication(client: AsyncClient, caregiver_with_patient: dict, medication_mock_data: dict):
    auth_headers = caregiver_with_patient["auth_headers"]
    patient_id = caregiver_with_patient["patient_id"]
    caregiver_id = caregiver_with_patient["caregiver_id"]
    medication_data = {**medication_mock_data, "user_id": patient_id}
    create_response = await client.post("/api/v1/medication", json=medication_data, headers=auth_headers)
    assert create_response.status_code == 201
    created_medication = create_response.json()
    response_read = await client.get("/api/v1/medication", headers=auth_headers)
    assert response_read.status_code == 200
    medication_list = response_read.json()
    assert len(medication_list) == 1
    assert medication_list[0]["id"] == created_medication["id"]
    assert medication_list[0]["author_id"] == caregiver_id

@pytest.mark.asyncio
async def test_update_medication(client: AsyncClient, caregiver_with_patient: dict, medication_mock_data: dict):
    auth_headers = caregiver_with_patient["auth_headers"]
    patient_id = caregiver_with_patient["patient_id"]
    medication_data = {**medication_mock_data, "user_id": patient_id}
    create_response = await client.post("/api/v1/medication", json=medication_data, headers=auth_headers)
    assert create_response.status_code == 201
    medication_id = create_response.json()["id"]
    update_data = {"dosage": "20 mg"}
    response = await client.patch(f"/api/v1/medication/{medication_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["dosage"] == "20 mg"


@pytest.mark.asyncio
async def test_medication_defaults_to_active(
    client: AsyncClient,
    caregiver_with_patient: dict,
    medication_mock_data: dict
):
    auth_headers = caregiver_with_patient["auth_headers"]
    patient_id = caregiver_with_patient["patient_id"]
    medication_data = {**medication_mock_data, "user_id": patient_id}   
    response = await client.post(
        "/api/v1/medication", json=medication_data, headers=auth_headers
    )
    assert response.status_code == 201
    # a newly created medication is active without the client sending a status
    assert response.json()["status"] == "active"


@pytest.mark.asyncio
async def test_discontinue_medication_keeps_record(
    client: AsyncClient,
    caregiver_with_patient: dict,
    medication_mock_data: dict
):
    auth_headers = caregiver_with_patient["auth_headers"]
    patient_id = caregiver_with_patient["patient_id"]
    medication_data = {**medication_mock_data, "user_id": patient_id}
    create_response = await client.post(
        "/api/v1/medication", json=medication_data, headers=auth_headers
    )
    assert create_response.status_code == 201
    medication_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/v1/medication/{medication_id}",
        json={"status": "discontinued"},
        headers=auth_headers
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


@pytest.mark.asyncio
async def test_cannot_create_medication_for_unassigned_patient(
    client: AsyncClient,
    medication_mock_data: dict
):
    # 1. A caregiver registers
    caregiver_data = {
        "first_name": "Care1", "last_name": "Giver1", "role": "caregiver",
        "email": "unassigned_caregiver_medication@example.com", "password": "securepassword123"
    }
    await client.post("/api/v1/users/create", json=caregiver_data)

    # 2. An unrelated patient registers
    patient_data = {
        "first_name": "Pat1", "last_name": "Ient1", "role": "patient",
        "email": "unassigned_patient_medication@example.com", "password": "securepassword123"
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
    medication_data = {**medication_mock_data, "user_id": patient_id}
    response = await client.post(
        "/api/v1/medication",
        json=medication_data,
        headers=auth_headers
    )

    # 5. verify_caregiver_access must refuse
    assert response.status_code == 403
    assert response.json()["detail"] == "You are not assigned to this patient"


@pytest.mark.asyncio
async def test_cannot_create_medication_about_self(
    client: AsyncClient,
    medication_mock_data: dict
):
    # 1. A caregiver registers — keep the id from the response
    caregiver_data = {
        "first_name": "Care2", "last_name": "Giver2", "role": "caregiver",
        "email": "self_author_medication@example.com", "password": "securepassword123"
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

    # 3. They try to write a medication about THEMSELVES
    medication_data = {**medication_mock_data, "user_id": caregiver_id}
    response = await client.post(
        "/api/v1/medication",
        json=medication_data,
        headers=auth_headers
    )

    # 4. The self-authoring guard must refuse
    assert response.status_code == 403
    assert response.json()["detail"] == "Records must be authored by a caregiver, not by the patient"


@pytest.mark.asyncio
async def test_cannot_update_medication_if_not_author(
    client: AsyncClient,
    caregiver_with_patient: dict,
    medication_mock_data: dict
):
    # 1. The assigned caregiver (author) creates the medication
    auth_headers_author = caregiver_with_patient["auth_headers"]
    patient_id = caregiver_with_patient["patient_id"]
    medication_data = {**medication_mock_data, "user_id": patient_id}

    create_response = await client.post(
        "/api/v1/medication", json=medication_data, headers=auth_headers_author
    )
    assert create_response.status_code == 201
    medication_id = create_response.json()["id"]

    # 2. A second caregiver registers
    other_caregiver_data = {
        "first_name": "Another1", "last_name": "Caregiver1", "role": "caregiver",
        "email": "not_the_author_medication@example.com", "password": "securepassword123"
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

    # 4. The second caregiver tries to update the medication they didn't author
    response = await client.patch(
        f"/api/v1/medication/{medication_id}",
        json={"dosage": "500 mg"},
        headers=auth_headers_other,
    )

    # 5. The server refuses (404: it doesn't confirm the record exists)
    assert response.status_code == 404
    assert response.json()["detail"] == "Medication not found"

    # 6. The data is unchanged: read as the author, the value is still the original
    read_response = await client.get("/api/v1/medication", headers=auth_headers_author)
    assert read_response.status_code == 200
    assert read_response.json()[0]["dosage"] == "10 mg"