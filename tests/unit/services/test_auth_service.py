from unittest.mock import AsyncMock, MagicMock

import pytest
from passlib.exc import UnknownHashError

from app.db.models import User
from app.db.repositories.user import UserRepository
from app.schemas.user import UserCreate
from app.services.auth import UserService, get_password_hash, verify_password


@pytest.fixture
def mock_repo():
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def user_service(mock_repo):
    return UserService(mock_repo)


@pytest.fixture
def sample_user_data():
    """Фикстура с тестовыми данными пользователя."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": get_password_hash("testpassword"),
        "password": "testpassword"
    }


@pytest.fixture
def sample_user_create(sample_user_data):
    """Фикстура для создания UserCreate объекта."""
    return UserCreate(
        username=sample_user_data["username"],
        email=sample_user_data["email"],
        password=sample_user_data["password"]
    )


# Тесты для утилитных функций
def test_verify_password_success(sample_user_data):
    """Проверка успешной верификации пароля."""
    hashed = sample_user_data["hashed_password"]
    assert verify_password(sample_user_data["password"], hashed)


def test_verify_password_failure(sample_user_data):
    """Проверка неудачной верификации пароля."""
    assert not verify_password("wrongpassword", sample_user_data["hashed_password"])


def test_verify_invalid_hash():
    """Проверка обработки невалидного хеша."""
    with pytest.raises(UnknownHashError):
        verify_password("test", "invalid_hash")


# Тесты для UserService
@pytest.mark.asyncio
async def test_create_user_success(user_service, mock_repo, sample_user_data, sample_user_create):
    """Успешное создание пользователя."""
    mock_repo.get_by_username.return_value = None
    mock_repo.get_by_email.return_value = None

    mock_user = MagicMock(spec=User)
    mock_user.id = 1
    mock_user.username = sample_user_data["username"]
    mock_user.email = sample_user_data["email"]
    mock_repo.create.return_value = mock_user

    result = await user_service.create_user(sample_user_create)

    assert result.id == 1
    mock_repo.create.assert_called_once()
    call_args = mock_repo.create.call_args[0][0]
    assert call_args["username"] == sample_user_data["username"]
    assert call_args["email"] == sample_user_data["email"]
    assert "hashed_password" in call_args


@pytest.mark.asyncio
async def test_create_user_duplicate_username(user_service, mock_repo):
    """Попытка создания пользователя с существующим username."""
    mock_repo.get_by_username.return_value = User(id=1, username="existing")

    with pytest.raises(ValueError, match="username уже существует"):
        await user_service.create_user(UserCreate(
            username="existing",
            email="new@example.com",
            password="password"
        ))


@pytest.mark.asyncio
async def test_create_user_duplicate_email(user_service, mock_repo):
    """Попытка создания пользователя с существующим email."""
    mock_repo.get_by_username.return_value = None
    mock_repo.get_by_email.return_value = User(id=1, email="existing@example.com")

    with pytest.raises(ValueError, match="email уже существует"):
        await user_service.create_user(UserCreate(
            username="newuser",
            email="existing@example.com",
            password="password"
        ))


@pytest.mark.asyncio
async def test_authenticate_user_success(user_service, mock_repo, sample_user_data):
    """Успешная аутентификация пользователя."""
    mock_user = MagicMock(spec=User)
    mock_user.hashed_password = sample_user_data["hashed_password"]
    mock_repo.get_by_username.return_value = mock_user

    result = await user_service.authenticate_user(
        sample_user_data["username"],
        sample_user_data["password"]
    )
    assert result is mock_user


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(user_service, mock_repo, sample_user_data):
    """Неудачная аутентификация из-за неверного пароля."""
    mock_user = MagicMock(spec=User)
    mock_user.hashed_password = sample_user_data["hashed_password"]
    mock_repo.get_by_username.return_value = mock_user

    result = await user_service.authenticate_user(
        sample_user_data["username"],
        "wrongpassword"
    )
    assert result is None


@pytest.mark.asyncio
async def test_authenticate_user_not_found(user_service, mock_repo, sample_user_data):
    """Попытка аутентификации несуществующего пользователя."""
    mock_repo.get_by_username.return_value = None

    result = await user_service.authenticate_user(
        sample_user_data["username"],
        sample_user_data["password"]
    )
    assert result is None


# Тесты на граничные случаи
@pytest.mark.asyncio
async def test_create_user_empty_password(user_service, mock_repo):
    """Попытка создания пользователя с пустым паролем."""
    mock_repo.get_by_username.return_value = None
    mock_repo.get_by_email.return_value = None

    with pytest.raises(ValueError):
        await user_service.create_user(UserCreate(
            username="newuser",
            email="new@example.com",
            password=""
        ))


@pytest.mark.asyncio
async def test_authenticate_user_empty_password(user_service, mock_repo):
    """Попытка аутентификации с пустым паролем."""
    test_user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("correct")
    )

    mock_repo.get_by_username.return_value = test_user

    result = await user_service.authenticate_user("testuser", "")
    assert result is None
