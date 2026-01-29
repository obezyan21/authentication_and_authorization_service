import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from app.services.users_service import UserService
from app.schemas.user_schemas import UserSchema


@pytest.fixture
def mock_user_data():
    mock_data = MagicMock()
    mock_data.email = "test@email.com"
    mock_data.name = "test"
    mock_data.surname = "test"
    mock_data.password = "123"
    mock_data.password_confirm = "123"
    mock_data.role = "User"
    return mock_data

@pytest.fixture
def mock_login_user_data():
    mock_data = MagicMock()
    mock_data.email = "test@email.com"
    mock_data.password = "123"
    return mock_data

@pytest.fixture
def mock_db_session():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    return mock_session

@pytest.fixture
def mock_active_user():
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.email = "test@email.com"
    mock_user.hashed_password = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
    mock_user.is_active = True
    mock_user.name = "Test"
    mock_user.surname = "User"
    mock_user.role = "User"
    return mock_user

@pytest.fixture
def mock_update_data():
    mock_data = MagicMock()
    mock_data.name = "test"
    mock_data.surname = "surname"
    mock_data.email = "test@email.com"
    return mock_data

@pytest.mark.asyncio
async def test_register_user_success(mock_db_session, mock_user_data):
    user_data = mock_user_data

    user_service = UserService(mock_db_session)

    result = await user_service.register_user(user_data)
    assert "id" in result
    assert result["email"] == user_data.email

@pytest.mark.asyncio
async def test_register_user_fail_pass_confirm(mock_db_session, mock_user_data):
    user_data = mock_user_data

    user_service = UserService(mock_db_session)

    user_data.password_confirm = "222" 
    with pytest.raises(HTTPException) as exc_err:
        await user_service.register_user(user_data)

    assert exc_err.value.status_code == 400

@pytest.mark.asyncio
async def test_register_user_exist(mock_user_data):
    user_data = mock_user_data

    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = True
    mock_session.execute.return_value = mock_result

    user_service = UserService(mock_session)

    with pytest.raises(HTTPException) as exc_err:
        await user_service.register_user(user_data)

    assert exc_err.value.status_code == 409

@pytest.mark.asyncio
async def test_login_user_success(mock_db_session, mock_login_user_data, mock_active_user):
    user_data = mock_login_user_data

    mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_active_user

    user_service = UserService(mock_db_session)

    with patch("app.services.users_service.verify_password") as mock_verify:
        mock_verify.return_value = True

        with patch("app.schemas.user_schemas.ResponseSchema.model_validate") as mock_validate:
            mock_response = MagicMock()
            mock_response.id = mock_active_user.id
            mock_response.name = mock_active_user.name
            mock_response.surname = mock_active_user.surname
            mock_response.email = mock_active_user.email
            mock_response.role = mock_active_user.role
            mock_response.is_active = mock_active_user.is_active
            mock_response.created_at = "now"
            mock_response.updated_at = "now"

            mock_validate.return_value = mock_response

            result = await user_service.login_user(user_data)

            assert result is not None
            assert result.email == mock_active_user.email
            assert result.id == mock_active_user.id

@pytest.mark.asyncio
async def test_login_user_not_found(mock_db_session, mock_login_user_data):
    user_data = mock_login_user_data

    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None

    user_service = UserService(mock_db_session)

    with pytest.raises(HTTPException) as exc_err:
        await user_service.login_user(user_data)

    assert exc_err.value.status_code == 404
    assert "Пользователь не найден" in str(exc_err.value.detail)

@pytest.mark.asyncio
async def test_login_user_fail_verify_password(mock_db_session, mock_login_user_data, mock_active_user):
    user_data = mock_login_user_data

    mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_active_user

    user_service = UserService(mock_db_session)
    with patch("app.services.users_service.verify_password") as mock_verify:
        mock_verify.return_value = False
        with pytest.raises(HTTPException) as exc_err:
            await user_service.login_user(user_data)

    assert exc_err.value.status_code == 401
    assert "Не правильный логин или пароль" in str(exc_err.value.detail)
    mock_verify.assert_called_once_with(user_data.password, mock_active_user.hashed_password)

@pytest.mark.asyncio
async def test_login_user_not_active(mock_db_session, mock_login_user_data, mock_active_user):
    user_data = mock_login_user_data

    mock_active_user.is_active = False

    mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_active_user

    user_service = UserService(mock_db_session)
    with patch("app.services.users_service.verify_password") as mock_verify:
        mock_verify.return_value = True
        with pytest.raises(HTTPException) as exc_err:
            await user_service.login_user(user_data)

    assert exc_err.value.status_code == 401
    assert "Пользователь неактивен" in str(exc_err.value.detail)

@pytest.mark.asyncio
async def test_update_user_succeess(mock_db_session, mock_active_user, mock_update_data):
    user_data = mock_update_data
    user_id = mock_active_user.id

    mock_select_result = MagicMock()
    mock_select_result.scalar_one_or_none.return_value = mock_active_user
    
    mock_update_result = MagicMock()
    mock_db_session.execute.side_effect = [
        mock_select_result,
        mock_update_result
    ]

    user_service = UserService(mock_db_session)
    result = await user_service.update_user(user_data, user_id)
    
    assert result == {"message": "Данные изменены"}
    mock_db_session.commit.assert_called_once()
    assert mock_db_session.execute.call_count == 2

@pytest.mark.asyncio
async def test_update_user_not_found(mock_db_session, mock_update_data):
    user_data = mock_update_data

    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    user_service = UserService(mock_db_session)
    with pytest.raises(HTTPException) as exc_err:
        await user_service.update_user(user_data, 999)
    
    assert exc_err.value.status_code == 404
    assert "Пользователь не найден" in str(exc_err.value.detail)

@pytest.mark.asyncio
async def test_update_user_not_active(mock_db_session, mock_active_user, mock_update_data):
    user_data = mock_update_data
    user_id = mock_active_user.id

    mock_active_user.is_active = False

    mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_active_user

    user_service = UserService(mock_db_session)
    with patch("app.services.users_service.verify_password") as mock_verify:
        mock_verify.return_value = True
        with pytest.raises(HTTPException) as exc_err:
            await user_service.update_user(user_data, user_id)

    assert exc_err.value.status_code == 401
    assert "Пользователь неактивен" in str(exc_err.value.detail)

@pytest.mark.asyncio
async def test_delete_user_success(mock_db_session, mock_active_user):
    user_id = mock_active_user.id

    mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_active_user

    user_service = UserService(mock_db_session)

    result = await user_service.delete_user(user_id)

    assert mock_active_user.is_active == False
    assert result == {"message": "Пользователь удален", "email": mock_active_user.email}
    mock_db_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_delete_user_not_found_or_deleted(mock_db_session):

    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None

    user_service = UserService(mock_db_session)

    with pytest.raises(HTTPException) as exc_err:
        await user_service.delete_user(999)

    assert exc_err.value.status_code == 404
    assert "Пользователь не найден или уже удален" in str(exc_err.value.detail)
