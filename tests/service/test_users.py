import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.services.users import UserService
from app.db.crud.users import UserCRUD
from app.schemas.users import UserCreate, UserUpdate
from app.db.models.users import User

@pytest.fixture
def user_service(async_db: AsyncSession):
    crud = UserCRUD(async_db)
    return UserService(db=async_db, crud=crud)

@pytest.mark.asyncio
async def test_service_create_user(user_service: UserService, user_mock_data: dict):
    user_in = UserCreate(**user_mock_data)
    
    user = await user_service.create_user(user_in)
    assert isinstance(user, User)
    assert user.email == user_in.email
    assert user.hashed_password is not None
    assert user.hashed_password != user_in.password

@pytest.mark.asyncio
async def test_service_create_user_duplicate_email(user_service: UserService, user_mock_data: dict):
    user_in = UserCreate(**user_mock_data)
    user_in.email = "duplicate@example.com"
    user_in.username = "duplicate1"
    
    await user_service.create_user(user_in)
    
    user_in.username = "duplicate2" 
    with pytest.raises(HTTPException) as exc:
        await user_service.create_user(user_in)
    
    assert exc.value.status_code == 400
    assert "already exists" in exc.value.detail

@pytest.mark.asyncio
async def test_service_update_user_not_found(user_service: UserService):
    update_data = UserUpdate(name="Test")
    
    with pytest.raises(HTTPException) as exc:
        await user_service.update_user(uuid.uuid4(), update_data)
        
    assert exc.value.status_code == 404
    assert "User not found" in exc.value.detail
