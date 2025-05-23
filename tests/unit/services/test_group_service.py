from unittest.mock import AsyncMock, MagicMock

import pytest

from app.db.models import Chat, Group
from app.db.repositories.chat import ChatRepository
from app.db.repositories.group import GroupRepository
from app.schemas.group import GroupCreate, GroupInfo, GroupList, GroupRead
from app.services.group import GroupService


@pytest.fixture
def mock_group_repo():
    return AsyncMock(spec=GroupRepository)


@pytest.fixture
def mock_chat_repo():
    return AsyncMock(spec=ChatRepository)


@pytest.fixture
def group_service(mock_group_repo, mock_chat_repo):
    return GroupService(mock_group_repo, mock_chat_repo)


@pytest.fixture
def sample_group_data():
    """Фикстура с тестовыми данными группы."""
    return {
        "name": "Test Group",
        "creator_id": 1,
        "members": [1],
        "chat_id": 1
    }


@pytest.fixture
def sample_group_create(sample_group_data):
    """Фикстура для создания GroupCreate объекта."""
    return GroupCreate(
        name=sample_group_data["name"],
        creator_id=sample_group_data["creator_id"]
    )


@pytest.mark.asyncio
async def test_create_group_success(group_service, mock_group_repo, mock_chat_repo, sample_group_data,
                                    sample_group_create):
    """Успешное создание группы."""
    mock_chat = MagicMock(spec=Chat)
    mock_chat.id = sample_group_data["chat_id"]
    mock_chat_repo.create.return_value = mock_chat

    mock_group = MagicMock(spec=Group)
    mock_group.id = 1
    mock_group.name = sample_group_data["name"]
    mock_group.creator_id = sample_group_data["creator_id"]
    mock_group.members = sample_group_data["members"]
    mock_group.chat_id = sample_group_data["chat_id"]
    mock_group.chat = mock_chat
    mock_group_repo.create.return_value = mock_group

    result = await group_service.create_group(sample_group_create)

    assert isinstance(result, GroupRead)
    mock_chat_repo.create.assert_called_once_with({
        "name": sample_group_data["name"],
        "is_group": True
    })
    mock_group_repo.create.assert_called_once_with({
        "name": sample_group_data["name"],
        "creator_id": sample_group_data["creator_id"],
        "members": [sample_group_data["creator_id"]],
        "chat_id": sample_group_data["chat_id"]
    })


@pytest.mark.asyncio
async def test_get_group_success(group_service, mock_group_repo, sample_group_data):
    """Успешное получение информации о группе."""
    mock_group = MagicMock(spec=Group)
    mock_group.id = 1
    mock_group.creator_id = sample_group_data["creator_id"]
    mock_group.members = sample_group_data["members"]
    mock_group_repo.get.return_value = mock_group

    result = await group_service.get_group(1)

    assert isinstance(result, GroupRead)
    assert result.creator_id == sample_group_data["creator_id"]
    assert result.members == sample_group_data["members"]


@pytest.mark.asyncio
async def test_get_group_not_found(group_service, mock_group_repo):
    """Группа не найдена."""
    mock_group_repo.get.return_value = None

    result = await group_service.get_group(999)
    assert result is None


@pytest.mark.asyncio
async def test_get_user_groups(group_service, mock_group_repo):
    """Получение списка групп пользователя."""
    mock_group1 = MagicMock()
    mock_group1.id = 1
    mock_group1.name = "Group 1"
    mock_group1.creator_id = 1
    mock_group1.members = [1, 2]
    mock_group1.chat_id = 1

    mock_group2 = MagicMock()
    mock_group2.id = 2
    mock_group2.name = "Group 2"
    mock_group2.creator_id = 1
    mock_group2.members = [1, 3]
    mock_group2.chat_id = 2

    mock_group_repo.get_user_groups.return_value = [mock_group1, mock_group2]

    result = await group_service.get_user_groups(1)

    assert isinstance(result, GroupList)
    assert len(result.groups) == 2
    assert all(isinstance(g, GroupInfo) for g in result.groups)


@pytest.mark.asyncio
async def test_add_member_success(group_service, mock_group_repo):
    """Успешное добавление участника."""
    mock_group = MagicMock(spec=Group)
    mock_group.members = [1]
    mock_group_repo.get.return_value = mock_group

    result = await group_service.add_member(1, 2)
    assert result is True
    mock_group_repo.update.assert_called_once_with(1, {"members": [1, 2]})


@pytest.mark.asyncio
async def test_add_existing_member(group_service, mock_group_repo):
    """Попытка добавить существующего участника."""
    mock_group = MagicMock(spec=Group)
    mock_group.members = [1, 2]
    mock_group_repo.get.return_value = mock_group

    result = await group_service.add_member(1, 2)
    assert result is False
    mock_group_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_remove_member_success(group_service, mock_group_repo):
    """Успешное удаление участника."""
    mock_group = MagicMock(spec=Group)
    mock_group.members = [1, 2]
    mock_group_repo.get.return_value = mock_group

    result = await group_service.remove_member(1, 2)
    assert result is True
    mock_group_repo.update.assert_called_once_with(1, {"members": [1]})


@pytest.mark.asyncio
async def test_remove_nonexistent_member(group_service, mock_group_repo):
    """Попытка удалить отсутствующего участника."""
    mock_group = MagicMock(spec=Group)
    mock_group.members = [1]
    mock_group_repo.get.return_value = mock_group

    result = await group_service.remove_member(1, 2)
    assert result is False
    mock_group_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_get_group_members(group_service, mock_group_repo):
    """Получение списка участников группы."""
    mock_group = MagicMock(spec=Group)
    mock_group.members = [1, 2, 3]
    mock_group_repo.get.return_value = mock_group

    result = await group_service.get_group_members(1)
    assert result == [1, 2, 3]


@pytest.mark.asyncio
async def test_get_group_members_not_found(group_service, mock_group_repo):
    """Получение участников несуществующей группы."""
    mock_group_repo.get.return_value = None

    result = await group_service.get_group_members(999)
    assert result == []
