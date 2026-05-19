import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.habit import Habit
from app.db.session import get_db
from fastapi import Depends


class HabitCRUD:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
    
    async def create_habit(self, obj_in: dict) -> Habit:
        db_object = Habit(**obj_in)
        self.db.add(db_object)
        await self.db.flush()
        return db_object

    async def habit_for_user(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[Habit]:
        result = await self.db.execute(select(Habit).where(Habit.user_id == user_id).offset(skip).limit(limit))
        return result.scalars().all()

    async def update_habit(self, db_object: Habit, obj_in: dict) -> Habit:
        for field, value in obj_in.items():
            if hasattr(db_object, field):
                setattr(db_object, field, value)
                await self.db.flush()
        return db_object
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[Habit]:
        result = await self.db.execute(select(Habit).offset(skip).limit(limit))
        return result.scalars().all()
    
    async def get_habit_by_id(self, habit_id: uuid.UUID) -> Habit | None:
        result = await self.db.execute(select(Habit).where(Habit.id == habit_id))
        return result.scalars().first()