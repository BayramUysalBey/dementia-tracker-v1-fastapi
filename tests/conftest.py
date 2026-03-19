import pytest
import pytest_asyncio
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from alembic.config import Config
from alembic import command
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.settings import settings
import app.db.session as db_session_module


TEST_DB_NAME = "test_dementia_db"
BASE_URL = settings.DATABASE_URL.rsplit('/', 1)[0] # cutting the real db name  => /my_db_name just want the address of the server.
TEST_DB_URL = f"{BASE_URL}/{TEST_DB_NAME}"
DEFAULT_DB_URL = f"{BASE_URL}/postgres"

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    administrator_engine = create_async_engine(DEFAULT_DB_URL, isolation_level="AUTOCOMMIT")    
    async with administrator_engine.connect() as conn:
        await conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
        await conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))
    await administrator_engine.dispose()

    original_url = settings.DATABASE_URL
    settings.DATABASE_URL = TEST_DB_URL
    
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)

    command.upgrade(alembic_cfg, "head")

    test_engine = create_async_engine(TEST_DB_URL, echo=False)
    db_session_module.engine = test_engine
    db_session_module.AsyncSessionLocal = async_sessionmaker(bind=test_engine)
    
    yield 
    
    await test_engine.dispose()
    settings.DATABASE_URL = original_url
    
    administrator_engine = create_async_engine(DEFAULT_DB_URL, isolation_level="AUTOCOMMIT")
    async with administrator_engine.connect() as conn:
        
		# neon.com/postgresql/postgresql-administration/postgresql-pg_terminate_backend
        await conn.execute(text(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{TEST_DB_NAME}'
            AND pid <> pg_backend_pid();
        """))
        await conn.execute(text(f"DROP DATABASE {TEST_DB_NAME}"))
    await administrator_engine.dispose()

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app) # Wrap the app in ASGITransport (httpx version issue and solution)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac