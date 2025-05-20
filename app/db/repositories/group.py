"""
Репозиторий для работы с групповыми чатами в базе данных.
Содержит методы для получения и управления группами.
Обеспечивает проверку прав доступа и валидацию операций с группами.
"""
from sqlalchemy import select, text

from app.db.models import Group
from app.db.repositories.base import BaseRepository


class GroupRepository(BaseRepository[Group]):
    """Репозиторий для работы с группами."""

    def __init__(self, session):
        super().__init__(Group, session)

    async def get(self, group_id: int) -> Group | None:
        """
        Получение группы по ID.

        Args:
            group_id: ID группы

        Returns:
            Group | None: Группа или None, если не найдена

        """
        query = select(Group).where(Group.id == group_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_groups(self, user_id: int) -> list[Group]:
        """
        Получение списка групп пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            list[Group]: Список групп

        """
        query = select(Group).where(text("CAST(members AS jsonb) @> CAST(:user_id AS jsonb)"))
        result = await self.session.execute(query, {"user_id": f"[{user_id}]"})
        return list(result.scalars().all())

    async def add_member(self, group_id: int, user_id: int) -> bool:
        """Добавление участника в группу."""
        group = await self.get(group_id)
        if not group or user_id in group.members:
            return False

        group.members.append(user_id)
        await self.session.commit()
        return True

    async def remove_member(self, group_id: int, user_id: int) -> bool:
        """Удаление участника из группы."""
        group = await self.get(group_id)
        if not group or user_id not in group.members:
            return False

        group.members.remove(user_id)
        await self.session.commit()
        return True

    async def is_member(self, user_id: int, group_id: int) -> bool:
        """Проверка участия пользователя в группе."""
        group = await self.get(group_id)
        return group is not None and user_id in group.members
