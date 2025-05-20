"""
Репозиторий для работы с чатами в базе данных.
Содержит методы для создания, получения и управления чатами.
Реализует проверку доступа пользователей к чатам и управление участниками.
Поддерживает как личные, так и групповые чаты.
"""

from sqlalchemy import alias, and_, select
from sqlalchemy.dialects.postgresql import JSONB

from app.db.models import Chat, Group, UserChat
from app.db.repositories.base import BaseRepository


class ChatRepository(BaseRepository[Chat]):
    """Репозиторий для работы с чатами."""

    def __init__(self, session):
        super().__init__(Chat, session)

    async def add_user_to_chat(self, chat_id: int, user_id: int) -> bool:
        """
        Добавление пользователя в чат.

        Args:
            chat_id: ID чата
            user_id: ID пользователя

        Returns:
            bool: True если пользователь успешно добавлен

        """
        result = await self.session.execute(
            select(UserChat)
            .where(and_(
                UserChat.chat_id == chat_id,
                UserChat.user_id == user_id
            ))
        )
        if result.scalar_one_or_none():
            return False

        user_chat = UserChat(
            chat_id=chat_id,
            user_id=user_id
        )
        self.session.add(user_chat)
        await self.session.commit()
        return True

    async def user_has_access(self, user_id: int, chat_id: int) -> bool:
        """
        Проверка доступа пользователя к чату.

        Для личных чатов проверяет связь в user_chats
        Для групповых чатов проверяет наличие в members группы
        """
        # Сначала проверяем личные чаты
        personal_chat_query = (
            select(Chat)
            .join(UserChat, Chat.id == UserChat.chat_id)
            .where(
                and_(
                    Chat.id == chat_id,
                    UserChat.user_id == user_id
                )
            )
        )
        result = await self.session.execute(personal_chat_query)
        if result.scalar_one_or_none():
            return True

        # Если это не личный чат, проверяем групповой чат
        group_chat_query = (
            select(Chat)
            .join(Group, Chat.id == Group.chat_id)
            .where(
                and_(
                    Chat.id == chat_id,
                    Group.members.cast(JSONB).contains([user_id])
                )
            )
        )
        result = await self.session.execute(group_chat_query)
        return result.scalar_one_or_none() is not None

    async def get_user_chats(self, user_id: int) -> list[Chat]:
        """
        Получение всех чатов пользователя:
        - личные чаты через user_chats
        - групповые чаты через members в Group.
        """
        query = (
            select(Chat)
            .join(UserChat, Chat.id == UserChat.chat_id)
            .where(UserChat.user_id == user_id)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_chat_by_id(self, chat_id: int) -> Chat | None:
        """Получение чата по ID."""
        query = select(Chat).where(Chat.id == chat_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_chat(self, name: str, is_group: bool = False) -> Chat:
        """Создание нового чата."""
        chat = Chat(name=name, is_group=is_group)
        self.session.add(chat)
        await self.session.commit()
        await self.session.refresh(chat)
        return chat

    async def remove_user_from_chat(self, user_id: int, chat_id: int) -> None:
        """Удаление пользователя из чата."""
        query = select(UserChat).where(
            and_(UserChat.user_id == user_id, UserChat.chat_id == chat_id)
        )
        result = await self.session.execute(query)
        user_chat = result.scalar_one_or_none()
        if user_chat:
            await self.session.delete(user_chat)
            await self.session.commit()

    async def check_chat_exists(self, user1_id: int, user2_id: int) -> bool:
        """
        Проверяет существование личного чата между двумя пользователями.

        Args:
            user1_id: ID первого пользователя
            user2_id: ID второго пользователя

        Returns:
            bool: True если чат существует, False если нет

        """
        uc1 = alias(UserChat, name='uc1')
        uc2 = alias(UserChat, name='uc2')

        subquery = (
            select(Chat.id)
            .join(uc1, Chat.id == uc1.c.chat_id)
            .join(uc2, Chat.id == uc2.c.chat_id)
            .where(
                and_(
                    Chat.is_group.is_(False),
                    uc1.c.user_id == user1_id,
                    uc2.c.user_id == user2_id
                )
            )
        ).exists()

        result = await self.session.execute(select(subquery))
        return result.scalar()
