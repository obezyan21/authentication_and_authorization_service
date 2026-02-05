from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.user_schemas import RoleEnum, UserSchema, LoginSchema, ResponseSchema, UpdateSchema
from app.schemas.permission_schemas import PermissionCreateSchema, PermissionResponseSchema, PermissionUpdateSchema, UserPermissionSchema


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

def test_perm_create_schema_valid():
    data = PermissionCreateSchema(
    role = RoleEnum.USER,
    resource = "products",
    action = "read",
    allowed = True
    )

    assert data.role == RoleEnum.USER
    assert isinstance(data.allowed, bool)

def test_perm_create_schema_invalid():
    with pytest.raises(ValidationError) as val_err:
        data = PermissionCreateSchema(
        role = "user",
        resource = "products",
        action = "read",
        allowed = 123
        )

    errors = val_err.value.errors()

    assert any("role" in error["loc"] for error in errors)
    assert any("allowed" in error["loc"] for error in errors)

def test_perm_update_schema_valid():
    data = PermissionUpdateSchema(
        allowed=True
    )

    assert isinstance(data.allowed, bool)

def test_perm_update_schema_invalid():
    with pytest.raises(ValidationError) as val_err:
        data = PermissionUpdateSchema(
        allowed=123
    )
        
    errors = val_err.value.errors()

    assert any("allowed" in error["loc"] for error in errors)

def test_perm_response_schema_valid():
    data = PermissionResponseSchema(
    id = 1,
    role = RoleEnum.USER,
    resource = "products",
    action = "read",
    allowed = True
    )

    assert isinstance(data.id, int)
    assert data.role == RoleEnum.USER
    assert isinstance(data.allowed, bool)

def test_perm_response_schema_invalid():
    with pytest.raises(ValidationError) as val_err:
        data = PermissionResponseSchema(
        id = "test",
        role = "123",
        resource = "products",
        action = "read",
        allowed = 123
        )

    errors = val_err.value.errors()

    assert any("id" in error["loc"] for error in errors)
    assert any("role" in error["loc"] for error in errors)
    assert any("allowed" in error["loc"] for error in errors)

def test_user_permission_schema_valid():
    data = UserPermissionSchema(
        resource = "products",
        action = "read",
        allowed = True
    )

    assert isinstance(data.allowed, bool)

def test_user_permission_schema_invalid():
    with pytest.raises(ValidationError) as val_err:
        data = UserPermissionSchema(
            resource = 1,
            action = 2,
            allowed = 3
        )
    
    errors = val_err.value.errors()

    assert any("resource" in error["loc"] for error in errors)
    assert any("action" in error["loc"] for error in errors)
    assert any("allowed" in error["loc"] for error in errors)
