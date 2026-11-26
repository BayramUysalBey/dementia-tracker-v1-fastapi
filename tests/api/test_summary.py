import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_assigned_caregiver_gets_summary(client: AsyncClient, caregiver_with_patient: dict):
    auth_headers = caregiver_with_patient["auth_headers"]
    patient_id = caregiver_with_patient["patient_id"]
    read_response = await client.get(f"/api/v1/patients/{patient_id}/summary", headers=auth_headers)
    assert read_response.status_code == 200, read_response.json()

@pytest.mark.asyncio
async def test_unassigned_caregiver_is_refused(client: AsyncClient, caregiver_with_patient: dict):
    auth_headers = caregiver_with_patient["auth_headers"]

    # A second patient who is NOT assigned to this caregiver
    other = {
        "first_name": "Other", "last_name": "Patient", "role": "patient",
        "email": "unassigned_summary_patient@example.com", "password": "securepassword123",
    }
    other_response = await client.post("/api/v1/users/create", json=other)
    assert other_response.status_code == 201
    other_patient_id = other_response.json()["id"]

    read_response = await client.get(f"/api/v1/patients/{other_patient_id}/summary", headers=auth_headers)
    assert read_response.status_code == 403
    assert read_response.json()["detail"] == "You are not assigned to this patient"

@pytest.mark.asyncio
async def test_summary_counts_the_patients_habits(
    client: AsyncClient, caregiver_with_patient: dict, habit_mock_data: dict
):
    auth_headers = caregiver_with_patient["auth_headers"]
    patient_id = caregiver_with_patient["patient_id"]

    habit_data = {**habit_mock_data, "user_id": patient_id}
    response_habit = await client.post(
            "/api/v1/habit",
            json=habit_data,
            headers=auth_headers
        )
    assert response_habit.status_code == 201
    
    read_response = await client.get(f"/api/v1/patients/{patient_id}/summary", headers=auth_headers)
    assert read_response.status_code == 200, read_response.json()["summary"]
    assert "1 habits" in read_response.json()["summary"]

@pytest.mark.asyncio
async def test_summary_counts_the_patients_medications(
    client: AsyncClient, caregiver_with_patient: dict, medication_mock_data: dict
):
    auth_headers = caregiver_with_patient["auth_headers"]
    patient_id = caregiver_with_patient["patient_id"]

    medication_data = {**medication_mock_data, "user_id": patient_id}
    response_medication = await client.post(
            "/api/v1/medication",
            json=medication_data,
            headers=auth_headers
        )
    assert response_medication.status_code == 201
    
    read_response = await client.get(f"/api/v1/patients/{patient_id}/summary", headers=auth_headers)
    assert read_response.status_code == 200, read_response.json()["summary"]
    assert "1 medications" in read_response.json()["summary"]

@pytest.mark.asyncio
async def test_summary_counts_the_patients_notes(
    client: AsyncClient, caregiver_with_patient: dict, note_mock_data: dict
):
    auth_headers = caregiver_with_patient["auth_headers"]
    patient_id = caregiver_with_patient["patient_id"]

    note_data = {**note_mock_data, "user_id": patient_id}
    response_note = await client.post(
            "/api/v1/note",
            json=note_data,
            headers=auth_headers
        )
    assert response_note.status_code == 201
    
    read_response = await client.get(f"/api/v1/patients/{patient_id}/summary", headers=auth_headers)
    assert read_response.status_code == 200, read_response.json()["summary"]
    assert "1 notes" in read_response.json()["summary"]

@pytest.mark.asyncio
async def test_summary_counts_the_patients_journals(
    client: AsyncClient, caregiver_with_patient: dict, journal_mock_data: dict
):
    auth_headers = caregiver_with_patient["auth_headers"]
    patient_id = caregiver_with_patient["patient_id"]

    journal_data = {**journal_mock_data, "user_id": patient_id}
    response_journal = await client.post(
            "/api/v1/journal",
            json=journal_data,
            headers=auth_headers
        )
    assert response_journal.status_code == 201
    
    read_response = await client.get(f"/api/v1/patients/{patient_id}/summary", headers=auth_headers)
    assert read_response.status_code == 200, read_response.json()["summary"]
    assert "1 journals" in read_response.json()["summary"]