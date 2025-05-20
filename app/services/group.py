"""
Сервис для работы с групповыми чатами.
Содержит бизнес-логику для создания и управления группами.
Реализует управление участниками групп и проверку прав доступа.
"""
from app.db.repositories.chat import ChatRepository
from app.db.repositories.group import GroupRepository
from app.schemas.group import GroupCreate, GroupInfo, GroupList, GroupRead


class GroupService:
    """Сервис для работы с групповыми чатами."""

    def __init__(self, group_repo: GroupRepository, chat_repo: ChatRepository):
        self.group_repo = group_repo
        self.chat_repo = chat_repo

    async def create_group(self, group_data: GroupCreate) -> GroupRead:
        """
        Создание новой группы.

        Args:
            group_data: Данные для создания группы

        Returns:
            GroupRead: Созданная группа

        """
        # Сначала создаётся чат
        chat = await self.chat_repo.create({
            "name": group_data.name,
            "is_group": True
        })

        # Затем создаётся группа с привязкой к чату
        group = await self.group_repo.create({
            "name": group_data.name,
            "creator_id": group_data.creator_id,
            "members": [group_data.creator_id],  # Создатель автоматически добавляется
            "chat_id": chat.id
        })

        # Добавляем связь с чатом
        group.chat = chat
        return GroupRead.from_orm(group)

    async def get_group(self, group_id: int) -> GroupRead | None:
        """
        Получение информации о группе.

        Args:
            group_id: ID группы

        Returns:
            GroupRead | None: Информация о группе или None, если группа не найдена

        """
        group = await self.group_repo.get(group_id)
        if not group:
            return None

        return GroupRead(
            id=group.id,
            creator_id=group.creator_id,
            members=group.members
        )

    async def get_user_groups(self, user_id: int) -> GroupList:
        """
        Получение списка групп пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            GroupList: Список групп пользователя

        """
        groups = await self.group_repo.get_user_groups(user_id)
        return GroupList(groups=[GroupInfo.from_orm(g) for g in groups])

    async def add_member(self, group_id: int, user_id: int) -> bool:
        """
        Добавление участника в группу.

        Args:
            group_id: ID группы
            user_id: ID пользователя

        Returns:
            bool: True если успешно, False если пользователь уже в группе

        """
        group = await self.group_repo.get(group_id)
        if not group or user_id in group.members:
            return False

        await self.group_repo.update(group_id, {
            "members": [*group.members, user_id]
        })
        return True

    async def remove_member(self, group_id: int, user_id: int) -> bool:
        """
        Удаление участника из группы.

        Args:
            group_id: ID группы
            user_id: ID пользователя

        Returns:
            bool: True если успешно, False если пользователя не было в группе

        """
        group = await self.group_repo.get(group_id)
        if not group or user_id not in group.members:
            return False

        await self.group_repo.update(group_id, {
            "members": [m for m in group.members if m != user_id]
        })
        return True

    async def get_group_members(self, group_id: int) -> list[int]:
        """
        Получение списка участников группы.

        Args:
            group_id: ID группы

        Returns:
            list[int]: Список ID участников

        """
        group = await self.group_repo.get(group_id)
        return group.members if group else []
