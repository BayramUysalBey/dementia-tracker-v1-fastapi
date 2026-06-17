from typing import List
from fastapi import APIRouter, Depends, status
from app.schemas.users import UserRead, UserCreate, UserUpdate
from app.db.models.users import User, UserRole
from app.services.users import UserService
from app.api.deps import get_current_user

router = APIRouter()

from fastapi import HTTPException

import logging
logger = logging.getLogger(__name__)


@router.post("/create", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate, 
    user_service: UserService = Depends(UserService)
):
    try:
        return await user_service.create_user(user_in)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error in create_user: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/me", response_model=UserRead)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.get("/", response_model=List[UserRead])
async def read_users(
    skip: int = 0, 
    limit: int = 100, 
    user_service: UserService = Depends(UserService),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.CAREGIVER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only caregivers can list all users"
        )
    users = await user_service.get_all_users(skip=skip, limit=limit)
    if not users:
        return []
        
    return list(users)

@router.patch("/me", response_model=UserRead)
async def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(UserService)
):
    return await user_service.update_user(current_user.id, user_in)
