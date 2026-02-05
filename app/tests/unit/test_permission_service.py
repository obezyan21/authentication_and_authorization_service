import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.unit.conftest import mock_db_session, mock_user_data
from app.services.permission_service import PermissionService
from app.schemas.user_schemas import RoleEnum


@pytest.fixture
def mock_permission():
    permission = MagicMock()
    permission.id = 1
    permission.role = RoleEnum.USER
    permission.resource = "products"
    permission.action = "Read"
    permission.allowed = True
    return permission

@pytest.mark.asyncio
async def test_check_permission_succes(mock_db_session, mock_user_data, mock_permission):
    user = mock_user_data
    resource = mock_permission.resource
    action = mock_permission.action
    
    mock_db_session.execute.side_effect = [
        Mock(scalar_one_or_none=Mock(return_value=user)),
        Mock(scalar_one_or_none=Mock(return_value=mock_permission))
    ]

    permission_service = PermissionService(mock_db_session)
    result = await permission_service.check_permission(user.id, resource, action)

    assert result is True

@pytest.mark.asyncio
async def test_check_permission_user_not_found(mock_db_session, mock_user_data, mock_permission):
    user = mock_user_data
    resource = mock_permission.resource
    action = mock_permission.action
    
    mock_db_session.execute.side_effect = [
        Mock(scalar_one_or_none=Mock(return_value=None)),
        Mock(scalar_one_or_none=Mock(return_value=None))
    ]

    permission_service = PermissionService(mock_db_session)
    
    with pytest.raises(HTTPException) as exc_err:
        await permission_service.check_permission(user.id, resource, action)

    assert exc_err.value.status_code == 404
    assert "Пользователь не найден или удален" in str(exc_err.value.detail)

@pytest.mark.asyncio
async def test_check_permission_user_not_active(mock_db_session, mock_user_data, mock_permission):
    user = mock_user_data
    user.is_active = False
    resource = mock_permission.resource
    action = mock_permission.action
    
    mock_db_session.execute.side_effect = [
        Mock(scalar_one_or_none=Mock(return_value=user)),
        Mock(scalar_one_or_none=Mock(return_value=None))
    ]

    permission_service = PermissionService(mock_db_session)
    
    with pytest.raises(HTTPException) as exc_err:
        await permission_service.check_permission(user.id, resource, action)

    assert exc_err.value.status_code == 404
    assert "Пользователь не найден или удален" in str(exc_err.value.detail)

@pytest.mark.asyncio
async def test_check_permission_permission_not_found(mock_db_session, mock_user_data, mock_permission):
    user = mock_user_data
    resource = mock_permission.resource
    action = mock_permission.action
    
    mock_db_session.execute.side_effect = [
        Mock(scalar_one_or_none=Mock(return_value=user)),
        Mock(scalar_one_or_none=Mock(return_value=None))
    ]

    permission_service = PermissionService(mock_db_session)
    
    with pytest.raises(HTTPException) as exc_err:
        await permission_service.check_permission(user.id, resource, action)

    assert exc_err.value.status_code == 404
    assert "Разрешение не найдено" in str(exc_err.value.detail)

@pytest.mark.asyncio
async def test_get_user_permissions_success(mock_db_session, mock_user_data):
    user = mock_user_data
    mock_permissions = [
        Mock(resource="products", action="read", allowed=True),
        Mock(resource="products", action="write", allowed=False)
    ]

    mock_db_session.execute.side_effect = [
        Mock(scalar_one_or_none=Mock(return_value=user)),
        Mock(scalars=Mock(return_value=Mock(all=Mock(return_value=mock_permissions))))
    ]

    mock_service = PermissionService(mock_db_session)

    result = await mock_service.get_user_permissions(user.id)

    for perm in result:
        assert "resource" in perm
        assert "action" in perm
        assert "allowed" in perm

@pytest.mark.asyncio
async def test_get_user_permissions_user_not_found(mock_db_session, mock_user_data):
    user = mock_user_data
    mock_permissions = [
        Mock(resource="products", action="read", allowed=True),
        Mock(resource="products", action="write", allowed=False)
    ]

    mock_db_session.execute.side_effect = [
        Mock(scalar_one_or_none=Mock(return_value=None)),
        Mock(scalars=Mock(return_value=Mock(all=Mock(return_value=mock_permissions))))
    ]

    mock_service = PermissionService(mock_db_session)

    with pytest.raises(HTTPException) as exc_err:
        await mock_service.get_user_permissions(user.id)

    assert exc_err.value.status_code == 404
    assert "Пользователь не найден или удален" in str(exc_err.value.detail)

@pytest.mark.asyncio
async def test_get_user_permissions_user_not_active(mock_db_session, mock_user_data):
    user = mock_user_data
    user.is_active = False
    mock_permissions = [
        Mock(resource="products", action="read", allowed=True),
        Mock(resource="products", action="write", allowed=False)
    ]

    mock_db_session.execute.side_effect = [
        Mock(scalar_one_or_none=Mock(return_value=user)),
        Mock(scalars=Mock(return_value=Mock(all=Mock(return_value=mock_permissions))))
    ]

    mock_service = PermissionService(mock_db_session)

    with pytest.raises(HTTPException) as exc_err:
        await mock_service.get_user_permissions(user.id)

    assert exc_err.value.status_code == 404
    assert "Пользователь не найден или удален" in str(exc_err.value.detail)

@pytest.mark.asyncio
async def test_get_all_permissions_success(mock_db_session):
    mock_permissions = [
        Mock(
            id=1,
            resource="products",
            action="read",
            allowed=True,
            role=RoleEnum.USER
        ),
        Mock(
            id=2,
            resource="products", 
            action="write",
            allowed=False,
            role=RoleEnum.USER
        )
    ]

    mock_db_session.execute.return_value.scalars.return_value.all.return_value = mock_permissions

    permission_service = PermissionService(mock_db_session)
    result = await permission_service.get_all_permissions()

    for perm in result:
        assert "id" in perm
        assert "role" in perm
        assert "resource" in perm
        assert "action" in perm
        assert "allowed" in perm

@pytest.mark.asyncio
async def test_create_permission_success(mock_db_session, mock_permission):
    role = RoleEnum.ADMIN
    resource = "products"
    action = "read"
    allowed = True

    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    
    permission_service = PermissionService(mock_db_session)
    result = await permission_service.create_permission(role, resource, action, allowed)

    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_awaited_once()
    mock_db_session.refresh.assert_awaited_once()

    add_args = mock_db_session.add.call_args[0][0]
    refresh_args = mock_db_session.refresh.call_args[0][0]
    assert add_args == refresh_args

    assert "id" in result
    assert "role" in result and result["role"] == role.value
    assert "resource" in result and result["resource"] == resource
    assert "action" in result and result["action"] == action
    assert "allowed" in result and result["allowed"] == allowed

@pytest.mark.asyncio
async def test_create_permission_exist(mock_db_session):
    role = RoleEnum.ADMIN
    resource = "products"
    action = "read"
    allowed = True

    mock_db_session.execute.return_value.scalar_one_or_none.return_value = True
    
    permission_service = PermissionService(mock_db_session)
    with pytest.raises(HTTPException) as exc_err:
        await permission_service.create_permission(role, resource, action, allowed)
    
    assert exc_err.value.status_code == 409
    assert f"Правило для роли {role.value}, ресурса {resource} и действия {action} уже существует" in str(exc_err.value.detail)

@pytest.mark.asyncio
async def test_update_permission_success(mock_permission, mock_db_session):
    permission_id = mock_permission.id

    mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_permission

    permission_service = PermissionService(mock_db_session)
    
    result = await permission_service.update_permission(permission_id, False)

    mock_db_session.commit.assert_awaited_once()
    mock_db_session.refresh.assert_awaited_once()

    assert result["id"] == permission_id
    assert result["allowed"] == False

@pytest.mark.asyncio
async def test_update_permission_not_found(mock_permission, mock_db_session):
    permission_id = mock_permission.id

    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None

    permission_service = PermissionService(mock_db_session)
    
    with pytest.raises(HTTPException) as exc_err:
        await permission_service.update_permission(permission_id, False)

    assert exc_err.value.status_code == 404
    assert "Правило доступа не найдено" in str(exc_err.value.detail)

@pytest.mark.asyncio
async def test_delete_permission_success(mock_permission, mock_db_session):
    permission_id = mock_permission.id

    mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_permission

    permission_service = PermissionService(mock_db_session)

    result = await permission_service.delete_permission(permission_id)
    
    mock_db_session.delete.assert_called_once_with(mock_permission)
    mock_db_session.commit.assert_awaited_once()
    assert "Правило доступа удалено" in result["message"]

@pytest.mark.asyncio
async def test_delete_permission_not_found(mock_permission, mock_db_session):
    permission_id = mock_permission.id

    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None

    permission_service = PermissionService(mock_db_session)

    with pytest.raises(HTTPException) as exc_err:
        await permission_service.delete_permission(permission_id)

    assert exc_err.value.status_code == 404
    assert "Правило доступа не найдено" in str(exc_err.value.detail)
