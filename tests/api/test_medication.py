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