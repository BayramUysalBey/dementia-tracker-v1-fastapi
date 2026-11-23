"""Seed demo data through the API.

Run once against an EMPTY local database. The script is not idempotent:
a second run stops at the first duplicate email (400).
"""
from pathlib import Path
import pandas as pd
import os
import httpx


DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "demo"

TABLES = ["users", "care_assignments", "habits", "medications"]   # in seeding order

BASE_URL = os.environ.get("SEED_BASE_URL", "http://localhost:8000")
if "fastapicloud" in BASE_URL:
    raise SystemExit("Refusing to seed production. Point SEED_BASE_URL at a local server.")

def load_csvs() -> dict[str, pd.DataFrame]:
    return {name: pd.read_csv(DATA_DIR / f"{name}.csv") for name in TABLES}

def create_users(client: httpx.Client, users: pd.DataFrame) -> dict[str, str]:
    """Create every user through the API; return {email: id}."""
    ids = {}
    for row in users.to_dict("records"):
        response = client.post("/api/v1/users/create", json=row)
        if response.status_code != 201:
            print(f"Failed for {row['email']} — Status: {response.status_code}, Body: {response.text}")
            response.raise_for_status()
        ids[row["email"]] = response.json()["id"]
    return ids

def login(client: httpx.Client, email: str, password: str) -> dict[str, str]:
    """Log in through the API; return the auth headers for later requests."""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": password},    # a form, so data=
    )
    if response.status_code != 200:
        print(f"Login failed for {email} — Status: {response.status_code}, Body: {response.text}")
        response.raise_for_status()
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def create_care_assignments(
    client: httpx.Client,
    assignments: pd.DataFrame,
    user_ids: dict[str, str],
    passwords: dict[str, str],
) -> None:
    """Each caregiver logs in and assigns their patients."""
    sessions: dict[str, dict[str, str]] = {}    # caregiver email -> auth headers
    for row in assignments.to_dict("records"):
        caregiver = row["caregiver_email"]
        if caregiver not in sessions:
            sessions[caregiver] = login(client, caregiver, passwords[caregiver])

        patient_id = user_ids[row["patient_email"]]
        response = client.post(
            "/api/v1/care-assignments",
            json={"patient_id": patient_id},
            headers=sessions[caregiver]
        )

        if response.status_code != 201:
            print(
                f"Failed to assign {row['patient_email']} to {caregiver} - "
                f"Status: {response.status_code}, Body: {response.text}" 
            )
            response.raise_for_status()

def create_records(
    client: httpx.Client,
    records: pd.DataFrame,
    endpoint: str,                          # "/api/v1/habit" or "/api/v1/medication"
    user_ids: dict[str, str],
    passwords: dict[str, str],
) -> None:
    """Each caregiver logs in and creates records about their patients."""
    sessions: dict[str, dict[str, str]] = {}
    for row in records.to_dict("records"):
        caregiver = row.pop("caregiver_email")
        patient_email = row.pop("patient_email")

        if caregiver not in sessions:
            sessions[caregiver] = login(client, caregiver, passwords[caregiver])

        body = {**row, "user_id": user_ids[patient_email]}

        response = client.post(
            endpoint,
            json=body,
            headers=sessions[caregiver]
        )
        if response.status_code != 201:
            print(
                f"Failed to POST to {endpoint} for {patient_email} - "
                f"Status: {response.status_code}. Body: {response.text}"
            )
            response.raise_for_status()

if __name__ == "__main__":
    tables = load_csvs()
    with httpx.Client(base_url=BASE_URL) as client:
        user_ids = create_users(client, tables["users"])
        passwords = dict(zip(tables["users"]["email"], tables["users"]["password"]))
        create_care_assignments(client, tables["care_assignments"], user_ids, passwords)
        print("Care assignments created:", len(tables["care_assignments"]))
        create_records(client, tables["habits"], "/api/v1/habit", user_ids, passwords)
        print("Habits created:", len(tables["habits"]))
        create_records(client, tables["medications"], "/api/v1/medication", user_ids, passwords)
        print("Medications created:", len(tables["medications"]))
    print(user_ids)