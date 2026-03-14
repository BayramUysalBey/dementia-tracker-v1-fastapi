import asyncio
from typing import AsyncGenerator
from sqlalchemy import MetaData, Table, Column, String 
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.settings import settings



meta = MetaData()
t1 = Table("t1", meta, Column("name", String(50), primary_key=True))

engine = create_async_engine(settings.DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def create_main():
	async with engine.begin() as conn:
		await conn.run_sync(meta.drop_all)
		await conn.run_sync(meta.create_all)



async def insert_objects(async_session: async_sessionmaker[AsyncSession]) -> None:
	async with async_session() as session:
         async with session.begin():
            session.add_all([])
			

async def get_db() -> AsyncGenerator[AsyncSession, None]:
	async with SessionLocal() as db:
		yield db