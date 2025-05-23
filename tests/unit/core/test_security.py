from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest

from app.core.security import create_access_token, decode_token
from app.schemas import TokenData


@pytest.fixture
def sample_token_data():
    """Фикстура с тестовыми данными для токена."""
    return TokenData(user_id='1')


@pytest.fixture
def sample_password():
    """Фикстура с тестовым паролем."""
    return "testpassword"


@pytest.mark.asyncio
async def test_create_access_token(sample_token_data):
    """Проверка создания JWT токена."""
    token = create_access_token(sample_token_data)
    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.asyncio
async def test_decode_token_success(sample_token_data):
    """Проверка успешного декодирования токена."""
    token = create_access_token(sample_token_data)
    decoded = decode_token(token)
    assert decoded is not None
    assert decoded['user_id'] == sample_token_data.user_id


@pytest.mark.asyncio
async def test_decode_token_invalid():
    """Проверка декодирования невалидного токена."""
    assert decode_token("invalid.token") is None


@pytest.mark.asyncio
async def test_decode_token_expired(sample_token_data):
    """Проверка декодирования просроченного токена."""
    with patch('app.core.security.datetime') as mock_datetime:
        test_now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
        mock_datetime.now.return_value = test_now - timedelta(days=1)  # Вчера

        token = create_access_token(sample_token_data)

    assert decode_token(token) is None


@pytest.mark.asyncio
async def test_decode_token_wrong_secret(sample_token_data):
    """Проверка декодирования токена с неправильным секретным ключом."""
    # Токен с правильным ключом
    token = create_access_token(sample_token_data)

    with patch('app.core.security.settings.auth.secret_key', new="wrong_secret"):
        assert decode_token(token) is None


@pytest.mark.asyncio
async def test_decode_token_wrong_algorithm(sample_token_data):
    """Проверка декодирования токена с неправильным алгоритмом."""
    # Токен с правильным алгоритмом
    token = create_access_token(sample_token_data)

    with patch('app.core.security.settings.auth.token_algorythm', new="HS384"):
        assert decode_token(token) is None
