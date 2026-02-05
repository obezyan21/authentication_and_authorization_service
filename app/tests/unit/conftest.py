import pytest
from unittest.mock import patch, MagicMock, AsyncMock, Mock
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user_schemas import RoleEnum


@pytest.fixture
def mock_user_data():
    mock_data = MagicMock()
    mock_data.email = "test@email.com"
    mock_data.name = "test"
    mock_data.surname = "test"
    mock_data.password = "123"
    mock_data.password_confirm = "123"
    mock_data.role = RoleEnum.USER
    return mock_data

@pytest.fixture
def mock_db_session():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result
    mock_session.commit = AsyncMock()
    mock_session.delete = Mock()
    mock_session.refresh = AsyncMock()
    return mock_session
