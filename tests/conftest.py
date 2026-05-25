import pytest
import pytest_asyncio
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from alembic.config import Config
from alembic import command
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.settings import settings
import app.db.session as db_session_module
import uuid
from app.api.deps import get_current_user
from app.db.models.users import User
from datetime import datetime, timezone
import tempfile


TEST_DB_NAME = settings.TEST_DB_NAME
BASE_URL = settings.DATABASE_URL.rsplit('/', 1)[0] if settings.DATABASE_URL else ""
TEST_DB_URL = f"{BASE_URL}/{TEST_DB_NAME}"
DEFAULT_DB_URL = f"{BASE_URL}/postgres"

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    async def create_database():
        administrator_engine = create_async_engine(DEFAULT_DB_URL, isolation_level="AUTOCOMMIT")    
        async with administrator_engine.connect() as conn:
            await conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
            await conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))
        await administrator_engine.dispose()
        
    asyncio.run(create_database())
    
    test_engine = create_async_engine(TEST_DB_URL, poolclass=NullPool, echo=False)
    db_session_module.engine = test_engine
    db_session_module.AsyncSessionLocal = async_sessionmaker(bind=test_engine)    
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
    command.upgrade(alembic_cfg, "head")

    yield 
    
    async def drop_database():
        await test_engine.dispose()
        dumper_engine = create_async_engine(DEFAULT_DB_URL, isolation_level="AUTOCOMMIT")
        async with dumper_engine.connect() as conn:
            await conn.execute(text(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{TEST_DB_NAME}' AND pid <> pg_backend_pid();
            """))
            await conn.execute(text(f"DROP DATABASE {TEST_DB_NAME}"))
        await dumper_engine.dispose()

    asyncio.run(drop_database())

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app) # Wrap the app in ASGITransport (httpx version issue and solution)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def async_db():
    from sqlalchemy.ext.asyncio import AsyncSession
    async with db_session_module.engine.connect() as conn:
        trans = await conn.begin()
        async_session = async_sessionmaker(conn, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            yield session
        await trans.rollback()

@pytest.fixture
def user_mock_data():
    unique_id = str(uuid.uuid4())[:8] 
    return {
        "first_name": "Simple",
        "last_name": "User",
        "role": "patient",
        "username": f"simpleuser_{unique_id}",
        "email": f"simple_{unique_id}@example.com",
        "password": "securepassword123"
    }

@pytest.fixture
def emergency_contact_mock_data():
    return {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "phone_number": "+1234567890",
        "relation": "Spouse",
        "is_primary": True
    }

@pytest.fixture
def medication_mock_data():
    return {
        "medication_type": "Pill",
        "medication_name": "Ebixa",
        "dosage": "10 mg"
	}

@pytest.fixture
def journal_mock_data():
    return { 
		"user_diary_entry": "I didn't forget to cook today",
		"author_diary_entry": "Her memory is better than yesterday"
	}

@pytest.fixture
def reminder_mock_data():
    return {
    "related_entity_id": str(uuid.uuid4()),      
    "related_entity_type": "medication",
    "name": "Take sleeping pill",
    "repeat": "daily",
    "type": "push",
    "check": "pending"
	}

@pytest.fixture
def habit_mock_data():
    return {
		"name": "Mom book",
        "target_frequency": "Daily",
        "streak_count": 3
	}

@pytest.fixture
def note_mock_data():
    
        return {
        "title": "Daily Process",
        "content": "Cooking meal plan",
        "category": "Mood",
        "type": "Syndrome",
        "is_checklist": True
    }


@pytest_asyncio.fixture
async def authenticated_client(client: AsyncClient):
    dummy_user = User(
        id=uuid.uuid4(), 
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        role="patient",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    app.dependency_overrides[get_current_user] = lambda: dummy_user
    yield client
    app.dependency_overrides.clear()
    
import tempfile

@pytest.fixture(autouse=True)
def override_upload_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = settings.MEDIA_UPLOAD_DIR
        settings.MEDIA_UPLOAD_DIR = temp_dir
        yield
        settings.MEDIA_UPLOAD_DIR = original_dir
