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



if __name__ == "__main__":
    tables = load_csvs()
    with httpx.Client(base_url=BASE_URL) as client:
        user_ids = create_users(client, tables["users"])
    print(user_ids)