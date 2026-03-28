import uuid
import random
from string import ascii_lowercase, digits
from typing import List, Optional
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud import users
from app.db.models.users import User
from app.schemas.users import UserCreate, UserUpdate

password_hashing = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
	return password_hashing.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
	return password_hashing.verify(password, hashed_password)

def random_username(email: str) -> str:
	random_first = email.split("@")[0]
	random_last = "".join(random.choices(f"{ascii_lowercase}{digits}", k=4))
	return f"{random_first}{random_last}"

async def create_user(db: AsyncSession, user_create: UserCreate) -> User:
	user_data = user_create.model_dump()

	password = user_data.pop("password")
	user_data["hashed_password"] = get_password_hash(password)

	if not user_data.get("username"):
		user_data["username"] = random_username(user_data["email"])
	return await users.create(db, user_data)

async def update_user(db: AsyncSession, user_id: uuid.UUID, user_create: UserUpdate) -> Optional[User]:
	db_object = await users.get_by_id(db, user_id)
	if not db_object:
		return None
	update_data = user_create.model_dump(exclude_unset=True)
	if "password" in update_data:
		password = update_data.pop("password")
		update_data["hashed_password"] = get_password_hash(password)
	return await users.update(db, db_object, update_data)

async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) ->Optional[User]:
	return await users.get_by_id(db, user_id)

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
	return await users.get_by_email(db, email)

async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 1000) -> List[User]:
	return await users.list_all(db, skip=skip, limit=limit)

async def get_current_user(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
	return await users.get_by_id(db, user_id)