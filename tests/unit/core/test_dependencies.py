from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.repositories.user import UserRepository


@pytest.fixture
def mock_db_session():
    return AsyncMock(spec=AsyncSession)


@pytest.mark.asyncio
async def test_get_current_user_success(mock_db_session):
    """Успешное получение текущего пользователя по валидному токену."""
    valid_token = "valid.token"
    user_id = 1

    mock_user_repo = AsyncMock(spec=UserRepository)
    mock_user_repo.get = AsyncMock(return_value=MagicMock())

    with (patch('app.core.dependencies.UserRepository', return_value=mock_user_repo),
          patch('app.core.dependencies.jwt.decode', return_value={"user_id": str(user_id)})):
        result = await get_current_user(token=valid_token, db=mock_db_session)

        assert result == user_id
        mock_user_repo.get.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_db_session):
    """Попытка получить пользователя с невалидным токеном."""
    invalid_token = "invalid.token"

    with patch('app.core.dependencies.jwt.decode', side_effect=JWTError("Invalid token")):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=invalid_token, db=mock_db_session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Недействительный токен"


@pytest.mark.asyncio
async def test_get_current_user_missing_user_id(mock_db_session):
    """Попытка получить пользователя с токеном без user_id."""
    token_without_user_id = "token.without.user.id"

    with patch('app.core.dependencies.jwt.decode', return_value={}):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token_without_user_id, db=mock_db_session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Токен не содержит ID пользователя"


@pytest.mark.asyncio
async def test_get_current_user_invalid_user_id_format(mock_db_session):
    """Попытка получить пользователя с токеном с некорректным форматом user_id."""
    token_with_invalid_user_id = "token.with.invalid.user.id"

    with patch('app.core.dependencies.jwt.decode', return_value={"user_id": "not_an_integer"}):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token_with_invalid_user_id, db=mock_db_session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Некорректный формат ID пользователя в токене"


@pytest.mark.asyncio
async def test_get_current_user_not_found(mock_db_session):
    """Попытка получить пользователя, которого нет в БД."""
    valid_token = "valid.token"
    user_id = 999

    mock_user_repo = AsyncMock(spec=UserRepository)
    mock_user_repo.get = AsyncMock(return_value=None)

    with (patch('app.core.dependencies.UserRepository', return_value=mock_user_repo),
          patch('app.core.dependencies.jwt.decode', return_value={"user_id": str(user_id)})):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=valid_token, db=mock_db_session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Пользователь не найден в БД"
        mock_user_repo.get.assert_called_once_with(user_id)
