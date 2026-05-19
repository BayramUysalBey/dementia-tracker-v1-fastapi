import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from app.schemas.habit import HabitCreate, HabitRead, HabitUpdate
from app.services.habit import HabitService
from app.api.deps import get_current_user
from app.db.models.habit import Habit
from app.db.models.users import User


router = APIRouter()


@router.post("", response_model=HabitRead, status_code=status.HTTP_201_CREATED)
async def create_habit(
    habit_in: HabitCreate,
    habit_service: HabitService = Depends(HabitService),
    current_user: User = Depends(get_current_user)
    ):
    return await habit_service.create_habit(habit_in, user_id=current_user.id)


@router.get("", response_model=List[HabitRead])
async def read_habit(
    skip: int = 0, 
    limit: int = 100,
    habit_service: HabitService = Depends(HabitService),
    current_user: User = Depends(get_current_user)
):
    habits = await habit_service.get_all_habit(user_id=current_user.id, skip=skip, limit=limit)
    if not habits:
        return []
        
    return list(habits)


@router.patch("/{habit_id}", response_model=HabitRead, status_code=status.HTTP_200_OK)
async def update_habit(
    habit_id: uuid.UUID,
    habit_in: HabitUpdate,
    current_user: User = Depends(get_current_user),
    habit_service: HabitService = Depends(HabitService)
):
    return await habit_service.update_habit(habit_id, current_user.id, habit_in)