import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.users import User


async def create(db: AsyncSession, object_in_data: dict) -> User:
    db_object = User(**object_in_data) # ** -> dictionary unpacking operator.
    db.add(db_object)
    await db.commit()
    await db.refresh(db_object)
    return db_object

async def get_by_id(db: AsyncSession, id: uuid.UUID) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == id))
    return result.scalar_one_or_none()

async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def list_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())

async def update(db: AsyncSession, db_object: User, object_in_data: dict) -> User:
    for user in object_in_data:
        if hasattr(db_object, user):
            setattr(db_object, user, object_in_data[user])            
    db.add(db_object)
    await db.commit()
    await db.refresh(db_object)
    return db_object