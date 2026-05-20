import pytest
from pydantic import ValidationError
from app.schemas.users import UserCreate, UserUpdate

def test_user_create_valid():
    user = UserCreate.model_validate({
        "first_name": "John",
        "last_name": "Doe",
        "role": "caregiver",
        "email": "john.doe@example.com",
        "username": "johndoe",
        "password": "securepassword123"
    })
    assert user.first_name == "John"
    assert user.role == "caregiver"

def test_user_create_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate.model_validate({
            "first_name": "John",
            "last_name": "Doe",
            "role": "caregiver",
            "email": "not-an-email",
            "username": "johndoe",
            "password": "securepassword123"
        })

def test_user_create_invalid_role():
    with pytest.raises(ValidationError):
        UserCreate.model_validate({
            "first_name": "John",
            "last_name": "Doe",
            "role": "admin",  # Invalid role
            "email": "john.doe@example.com",
            "username": "johndoe",
            "password": "securepassword123"
        })

def test_user_update_optional_fields():
    user_update = UserUpdate.model_validate({"first_name": "Jane"})
    assert user_update.first_name == "Jane"
    assert user_update.last_name is None
    assert user_update.username is None
