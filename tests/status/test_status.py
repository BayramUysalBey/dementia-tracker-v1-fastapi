import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_root_message(client: AsyncClient):
    response = await client.get("/api/v1/status/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Dementia Tracker V1 API"}

@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/api/v1/status/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "connected"
