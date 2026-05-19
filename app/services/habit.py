from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import  Depends
from app.db.session import get_db
from app.db.crud.habit import HabitCRUD
from app.db.models.habit import Habit
from app.schemas.habit import HabitCreate, HabitUpdate
import uuid
from fastapi import HTTPException, status, Depends


class HabitService:
    def __init__(
        self, 
        db: AsyncSession = Depends(get_db), 
        crud: HabitCRUD = Depends(HabitCRUD)
    ):
        self.db = db
        self.crud = crud
        
    async def create_habit(self, create_in: HabitCreate, user_id: uuid.UUID) -> Habit:
        create_data = create_in.model_dump()
        create_data["user_id"] = user_id
        habit = await self.crud.create_habit(create_data)
        await self.db.refresh(habit)
        return habit
        
    async def get_all_habit(self, user_id: uuid.UUID, skip: int = 0, limit: int = 1000) -> Sequence[Habit]:
        return await self.crud.habit_for_user(user_id=user_id, skip=skip, limit=limit)
    
    async def update_habit(self, habit_id: uuid.UUID, user_id: uuid.UUID, user_in: HabitUpdate) -> Habit:
        db_object = await self.crud.get_habit_by_id(habit_id)
        if not db_object or db_object.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
        update_data = user_in.model_dump(exclude_unset=True)
        updated_habit = await self.crud.update_habit(db_object, update_data)
        await self.db.refresh(updated_habit)
        return updated_habit