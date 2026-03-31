import uuid
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.users import UserRead, UserCreate, UserUpdate
from app.db.models.users import User
from app.services.users import UserService
from app.db.session import get_db
from app.db.crud.users import UserCRUD

router = APIRouter()

async def get_user_crud(db: AsyncSession = Depends(get_db)) -> UserCRUD:
    return UserCRUD(db)

async def get_user_service(
    db: AsyncSession = Depends(get_db), 
    crud: UserCRUD = Depends(get_user_crud)
) -> UserService:
    return UserService(db, crud)

async def get_user(
    secret_user_id: uuid.UUID | None = Header(default=None, description="Temporary auth via Secret-User-Id"),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """Dependency to look up a user and ensure they exist."""
    if not secret_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header Secret-User-Id is required for temporary authentication"
        )
    user = await user_service.get_current_user(secret_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/create", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate, 
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.create_user(user_in)

@router.get("/me", response_model=UserRead)
async def read_user_me(
    current_user: User = Depends(get_user)
):
    return current_user



@router.get("/", response_model=List[UserRead])
async def read_users(
    skip: int = 0, 
    limit: int = 100, 
    user_service: UserService = Depends(get_user_service)
):
    users = await user_service.get_all_users(skip=skip, limit=limit)
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found"
        )
    return list(users)

@router.patch("/me", response_model=UserRead)
async def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_user),
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.update_user(current_user.id, user_in)
