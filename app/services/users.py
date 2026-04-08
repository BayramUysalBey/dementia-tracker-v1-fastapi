import uuid
import random
from string import ascii_lowercase, digits
from typing import Sequence
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Depends, Header
from app.db.session import get_db

from app.db.crud.users import UserCRUD
from app.db.models.users import User
from app.schemas.users import UserCreate, UserUpdate

password_hashing = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(
        self, 
        db: AsyncSession = Depends(get_db), 
        crud: UserCRUD = Depends(UserCRUD)
    ):
        self.db = db
        self.crud = crud

	

    def get_password_hash(self, password: str) -> str:
        return password_hashing.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return password_hashing.verify(password, hashed_password)

    def random_username(self, email: str) -> str:
        random_first = email.split("@")[0]
        random_last = "".join(random.choices(f"{ascii_lowercase}{digits}", k=4))
        return f"{random_first}{random_last}"
    

    async def create_user(self, user_in: UserCreate) -> User:
        existing_user = await self.crud.get_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
            
        hashed_password = self.get_password_hash(user_in.password)
        generated_username = user_in.username or self.random_username(user_in.email)
        
        create_data = user_in.model_dump(exclude={"password"})
        create_data["hashed_password"] = hashed_password
        create_data["username"] = generated_username
        
        user = await self.crud.create(create_data)
        await self.db.refresh(user)
        return user

    async def update_user(self, user_id: uuid.UUID, user_in: UserUpdate) -> User:
        db_object = await self.crud.get_by_id(user_id)
        if not db_object:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        update_data = user_in.model_dump(exclude_unset=True)
        
        if "password" in update_data:
            hashed_password = self.get_password_hash(update_data.pop("password"))
            update_data["hashed_password"] = hashed_password
            
        protected_fields = {"id", "email", "last_login", "created_at", "updated_at"}
        for field in protected_fields:
            update_data.pop(field, None)
            
        updated_user = await self.crud.update(db_object, update_data)
        await self.db.refresh(updated_user)
        return updated_user

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self.crud.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.crud.get_by_email(email)

    async def get_all_users(self, skip: int = 0, limit: int = 1000) -> Sequence[User]:
        return await self.crud.list_all(skip=skip, limit=limit)
        
async def get_current_user(
    secret_user_id: uuid.UUID | None = Header(default=None, description="Temporary auth via Secret-User-Id"),
    user_service: UserService = Depends(UserService)
) -> User:
    if not secret_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header Secret-User-Id is required for temporary authentication"
        )
    user = await user_service.get_user_by_id(secret_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

