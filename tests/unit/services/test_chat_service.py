from unittest.mock import AsyncMock, MagicMock

import pytest

from app.db.models import Chat
from app.db.repositories.chat import ChatRepository
from app.schemas.chat import ChatCreate, ChatRead
from app.services.chat import ChatService


@pytest.fixture
def mock_repo():
    return AsyncMock(spec=ChatRepository)


@pytest.fixture
def chat_service(mock_repo):
    return ChatService(mock_repo)


@pytest.fixture
def sample_chat_data():
    """Фикстура с тестовыми данными личного чата."""
    return {
        "name": "Test Chat",
        "is_group": False,
        "current_user_id": 1,
        "user_id": 2
    }


@pytest.fixture
def sample_chat_create(sample_chat_data):
    """Фикстура для создания ChatCreate объекта."""
    return ChatCreate(
        name=sample_chat_data["name"],
        is_group=sample_chat_data["is_group"],
        current_user_id=sample_chat_data["current_user_id"],
        user_id=sample_chat_data["user_id"]
    )


@pytest.mark.asyncio
async def test_create_chat_success(chat_service, mock_repo, sample_chat_data, sample_chat_create):
    """Успешное создание чата."""
    mock_repo.check_chat_exists.return_value = False

    mock_chat = MagicMock(spec=Chat)
    mock_chat.id = 1
    mock_chat.name = sample_chat_data["name"]
    mock_chat.is_group = sample_chat_data["is_group"]
    mock_repo.create.return_value = mock_chat

    result = await chat_service.create_chat(sample_chat_create)

    assert isinstance(result, ChatRead)
    mock_repo.create.assert_called_once()
    assert mock_repo.add_user_to_chat.call_count == 2
    assert sample_chat_create.name == f"Personal Chat {sample_chat_data['user_id']}"


@pytest.mark.asyncio
async def test_create_group_chat(chat_service, mock_repo):
    """Создание группового чата."""
    chat_data = ChatCreate(
        name="Group Chat",
        is_group=True,
        current_user_id=1,
        user_id=2
    )

    mock_repo.check_chat_exists.return_value = False

    mock_chat = MagicMock(spec=Chat)
    mock_chat.id = 1
    mock_chat.name = "Group Chat"
    mock_chat.is_group = True
    mock_repo.create.return_value = mock_chat

    result = await chat_service.create_chat(chat_data)

    assert result.is_group
    assert chat_data.name == "Group Chat"  # Имя не должно измениться


@pytest.mark.asyncio
async def test_create_existing_chat(chat_service, mock_repo, sample_chat_create):
    """Попытка создания существующего чата."""
    mock_repo.check_chat_exists.return_value = True

    with pytest.raises(ValueError, match="Личный чат между этими пользователями уже существует"):
        await chat_service.create_chat(sample_chat_create)
