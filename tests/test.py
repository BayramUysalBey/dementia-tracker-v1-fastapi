import uuid
import pytest
from httpx import AsyncClient
from app.main import app
from app.db.models.users import User

@pytest.mark.asyncio
async def test_root_message(client: AsyncClient):
    # The routers were restructured under a master router at /api/v1
    response = await client.get("/api/v1/status/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Dementia Tracker V1 API"}

@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/api/v1/status/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "connected"