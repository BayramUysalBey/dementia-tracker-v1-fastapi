import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.users import User
from app.schemas.users import UserCreate, UserUpdate

class UserCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, obj_in: dict) -> User:
        db_object = User(**obj_in)
        self.db.add(db_object)
        await self.db.flush()
        return db_object

    async def get_by_id(self, id: uuid.UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[User]:
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()

    async def update(self, db_object: User, obj_in: dict) -> User:
        for field, value in obj_in.items():
            if hasattr(db_object, field):
                setattr(db_object, field, value)
                
        self.db.add(db_object)
        await self.db.flush()
        return db_object