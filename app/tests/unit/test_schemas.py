from datetime import datetime, timezone

import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from app.services.users_service import UserService
from app.schemas.user_schemas import RoleEnum, UserSchema, LoginSchema, ResponseSchema, UpdateSchema

def test_user_schema_valid():
    user = UserSchema(
        name = "test",
        surname = "test",
        email = "test@email.com",
        password = "123",
        password_confirm = "123",
        role = "Пользователь"
    )
    
    assert user.email == "test@email.com"
    assert user.role == RoleEnum.USER
    
    user.role = "Читатель"
    assert user.role == RoleEnum.VIEWER
    
    user.role = "Менеджер"
    assert user.role == RoleEnum.MANAGER

    user.role = "Администратор"
    assert user.role == RoleEnum.ADMIN


def test_user_schema_invalid():
    with pytest.raises(ValidationError) as val_err:
        UserSchema(
            name = "test",
            surname = "test",
            email = "test",
            password = "test",
            password_confirm = "test",
            role = "test"
        )

    errors = val_err.value.errors()
    assert any("email" in error["loc"] for error in errors)
    assert any("role" in error["loc"] for error in errors)

def test_login_schema_valid():
        login_data = LoginSchema(
            email= "test@email.com",
            password= "test"
        )
        assert login_data.email == "test@email.com"

def test_login_schema_invalid():
    with pytest.raises(ValidationError) as val_err:
        LoginSchema(
            email= "test",
            password= "test"
        )
        
    errors = val_err.value.errors()
    assert any("email" in error["loc"] for error in errors)

def test_response_schema_valid():
    data = ResponseSchema(
        id = 1,
        name = "test",
        surname = "test",
        email = "test@email.com",
        role = RoleEnum.USER,
        is_active = True,
        created_at = datetime.now(timezone.utc),
        updated_at = datetime.now(timezone.utc)
    )
    assert data.email == "test@email.com"
    assert data.role == RoleEnum.USER

def test_response_schema_invalid():
    with pytest.raises(ValidationError) as val_err:
        data = ResponseSchema(
            id = 1,
            name = "test",
            surname = "test",
            email = "test",
            role = "test",
            is_active = True,
            created_at = datetime.now(timezone.utc),
            updated_at = datetime.now(timezone.utc)
        )
    errors = val_err.value.errors()
    assert any("email" in error["loc"] for error in errors)
    assert any("role" in error["loc"] for error in errors)

def test_update_schema_valid():
    data = UpdateSchema(
        name = "test",
        surname = "test",
        email = "test@email.com"
    )

    assert data.email == "test@email.com"

def test_update_schema_invalid():
    with pytest.raises(ValidationError) as val_err:
        data = UpdateSchema(
        name = "test",
        surname = "test",
        email = "test"
    )
    
    errors = val_err.value.errors()
    assert any("email" in error["loc"] for error in errors)
