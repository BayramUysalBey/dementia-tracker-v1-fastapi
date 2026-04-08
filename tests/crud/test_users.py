import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud.users import UserCRUD
from app.db.models.users import User
import uuid

@pytest.mark.asyncio
async def test_crud_create_user(async_db: AsyncSession, user_mock_data: dict):
    req_crud = UserCRUD(async_db)
    
    create_data = user_mock_data.copy()
    create_data.pop("password")
    create_data["hashed_password"] = "crud_hashed_secure"
    
    new_user = await req_crud.create(create_data)
    
    assert isinstance(new_user, User)
    assert new_user.email == user_mock_data["email"]
    assert new_user.id is not None
    
@pytest.mark.asyncio
async def test_crud_get_by_id(async_db: AsyncSession, user_mock_data: dict):
    req_crud = UserCRUD(async_db)
    
    create_data = user_mock_data.copy()
    create_data.pop("password")
    create_data["hashed_password"] = "crud_hashed_secure"
    create_data["email"] = "getbyid@example.com"
    create_data["username"] = "getbyid_user"
    new_user = await req_crud.create(create_data)
    
    user_in_db = await req_crud.get_by_id(new_user.id)
    assert isinstance(user_in_db, User)
    assert user_in_db.id == new_user.id

@pytest.mark.asyncio
async def test_crud_get_by_id_not_found(async_db: AsyncSession): 
    req_crud = UserCRUD(async_db)
    
    user_in_db = await req_crud.get_by_id(uuid.uuid4())
    assert user_in_db is None

@pytest.mark.asyncio
async def test_crud_update_user(async_db: AsyncSession, user_mock_data: dict):
    req_crud = UserCRUD(async_db)
    
    create_data = user_mock_data.copy()
    create_data.pop("password")
    create_data["hashed_password"] = "crud_hashed_secure"
    create_data["email"] = "update@example.com"
    create_data["username"] = "update_user"
    new_user = await req_crud.create(create_data)
    
    update_data = {"name": "Updated Name"}
    updated_user = await req_crud.update(new_user, update_data)
    
    assert updated_user.name == "Updated Name"
    assert updated_user.id == new_user.id
