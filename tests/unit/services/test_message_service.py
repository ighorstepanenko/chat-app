import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.message import MessageRead
from app.services.message import MessageService


@pytest.fixture
def mock_message_repo():
    return AsyncMock()


@pytest.fixture
def mock_chat_repo():
    return AsyncMock()


@pytest.fixture
def message_service(mock_message_repo, mock_chat_repo):
    return MessageService(mock_message_repo, mock_chat_repo)


@pytest.fixture
def sample_message_data():
    return {
        "chat_id": 1,
        "sender_id": 1,
        "text": "Test message",
        "is_read": False
    }


@pytest.mark.asyncio
async def test_send_message_success(message_service, mock_message_repo, mock_chat_repo, sample_message_data):
    """Успешная отправка сообщения."""
    mock_chat_repo.user_has_access.return_value = True

    mock_message = MagicMock()
    mock_message.id = 1
    mock_message.chat_id = sample_message_data["chat_id"]
    mock_message.sender_id = sample_message_data["sender_id"]
    mock_message.text = sample_message_data["text"]
    mock_message.is_read = sample_message_data["is_read"]
    mock_message_repo.create.return_value = mock_message

    result = await message_service.send_message(
        chat_id=sample_message_data["chat_id"],
        sender_id=sample_message_data["sender_id"],
        text=sample_message_data["text"]
    )

    assert isinstance(result, MessageRead)
    mock_message_repo.create.assert_called_once_with({
        "chat_id": sample_message_data["chat_id"],
        "sender_id": sample_message_data["sender_id"],
        "text": sample_message_data["text"]
    })


@pytest.mark.asyncio
async def test_send_message_no_access(message_service, mock_chat_repo):
    """Попытка отправки сообщения без доступа к чату."""
    mock_chat_repo.user_has_access.return_value = False

    with pytest.raises(ValueError, match="не имеет доступа к этому чату"):
        await message_service.send_message(1, 1, "Test")


@pytest.mark.asyncio
async def test_get_chat_history_success(message_service, mock_message_repo, mock_chat_repo):
    """Успешное получение истории сообщений."""
    mock_chat_repo.user_has_access.return_value = True

    mock_message1 = MagicMock()
    mock_message1.id = 1
    mock_message1.text = "Message 1"

    mock_message2 = MagicMock()
    mock_message2.id = 2
    mock_message2.text = "Message 2"

    mock_message_repo.get_chat_messages.return_value = [mock_message1, mock_message2]

    result = await message_service.get_chat_history(1, 1)

    assert len(result) == 2
    assert all(isinstance(msg, MessageRead) for msg in result)
    assert result[0].text == "Message 1"
    assert result[1].text == "Message 2"


@pytest.mark.asyncio
async def test_get_chat_history_no_access(message_service, mock_chat_repo):
    """Попытка получить историю без доступа к чату."""
    mock_chat_repo.user_has_access.return_value = False

    with pytest.raises(ValueError, match="не имеет доступа к этому чату"):
        await message_service.get_chat_history(1, 1)


@pytest.mark.asyncio
async def test_mark_as_read_success(message_service, mock_message_repo):
    """Успешная пометка сообщения как прочитанного."""
    mock_message_repo.mark_as_read.return_value = True

    result = await message_service.mark_as_read(1)
    assert result is True


@pytest.mark.asyncio
async def test_mark_as_read_failure(message_service, mock_message_repo):
    """Попытка пометить несуществующее сообщение."""
    mock_message_repo.mark_as_read.return_value = False

    result = await message_service.mark_as_read(999)
    assert result is False


@pytest.mark.asyncio
async def test_concurrent_message_sending(message_service, mock_message_repo, mock_chat_repo):
    """Проверка блокировки при одновременной отправке."""
    mock_chat_repo.user_has_access.return_value = True

    # Счетчик вызовов и список для временных меток
    call_count = 0
    call_times = []

    async def mock_create(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        call_times.append(asyncio.get_event_loop().time())

        # Имитация долгой операции
        await asyncio.sleep(0.1)

        mock_message = MagicMock()
        mock_message.id = 1
        mock_message.chat_id = 1
        mock_message.sender_id = 1
        mock_message.text = "Test message"
        mock_message.is_read = False
        return mock_message

    mock_message_repo.create.side_effect = mock_create

    # Запуск двух "конкурентных" отправок
    task1 = asyncio.create_task(message_service.send_message(1, 1, "Msg1"))
    task2 = asyncio.create_task(message_service.send_message(1, 1, "Msg2"))

    await asyncio.gather(task1, task2)

    assert call_count == 2
    assert call_times[1] - call_times[0] >= 0.1
