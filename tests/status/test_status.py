import pytest
from httpx import AsyncClient
from sqlalchemy.exc import SQLAlchemyError
from app.main import app
from app.db.session import get_db

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

class _BrokenSession:
    """Stands in for an AsyncSession whose connection is dead."""

    async def execute(self, *args, **kwargs):
        raise SQLAlchemyError("simulated database outage")


async def _broken_get_db(): # _: private to this file, not a test, not for import elsewhere
    yield _BrokenSession()


@pytest.mark.asyncio
async def test_health_returns_503_when_database_unreachable(client: AsyncClient):
    app.dependency_overrides[get_db] = _broken_get_db
    try:
        response = await client.get("/api/v1/status/health")

        assert response.status_code == 503
        body = response.json()
        assert body["status"] == "error"
        assert body["database"] == "unconnected"
    finally:
        app.dependency_overrides.pop(get_db, None)