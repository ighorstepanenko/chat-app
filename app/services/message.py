"""
Сервис для работы с сообщениями.
Содержит бизнес-логику для отправки и получения сообщений.
Реализует проверку прав доступа и управление статусом сообщений.
"""

import asyncio

from app.db.repositories.chat import ChatRepository
from app.db.repositories.message import MessageRepository
from app.schemas.message import MessageRead


class MessageService:
    """Сервис для работы с сообщениями."""

    def __init__(self, message_repo: MessageRepository, chat_repo: ChatRepository):
        self.message_repo = message_repo
        self.chat_repo = chat_repo
        self.lock = asyncio.Lock()  # Для предотвращения дублирования сообщений

    async def send_message(self, chat_id: int, sender_id: int, text: str) -> MessageRead:
        """
        Отправка сообщения в чат.

        Args:
            chat_id: ID чата
            sender_id: ID отправителя
            text: Текст сообщения

        Returns:
            MessageRead: Отправленное сообщение

        """
        async with self.lock:
            if not await self._user_has_access(sender_id, chat_id):
                msg = "Пользователь не имеет доступа к этому чату"
                raise ValueError(msg)

            message = await self.message_repo.create({
                "chat_id": chat_id,
                "sender_id": sender_id,
                "text": text
            })
            return MessageRead.from_orm(message)

    async def get_chat_history(
            self, chat_id: int, user_id: int, limit: int = 100, offset: int = 0
    ) -> list[MessageRead]:
        """
        Получение истории сообщений чата.

        Args:
            chat_id: ID чата
            user_id: ID пользователя (для проверки доступа)
            limit: Количество сообщений
            offset: Смещение

        Returns:
            list[MessageRead]: Список сообщений

        """
        if not await self._user_has_access(user_id, chat_id):
            msg = "Пользователь не имеет доступа к этому чату"
            raise ValueError(msg)

        messages = await self.message_repo.get_chat_messages(chat_id, limit, offset)
        return [MessageRead.from_orm(msg) for msg in messages]

    async def mark_as_read(self, message_id: int) -> bool:
        """
        Пометка сообщения как прочитанного.

        Args:
            message_id: ID сообщения

        Returns:
            bool: True если успешно, False если сообщение не найдено

        """
        return await self.message_repo.mark_as_read(message_id)

    async def _user_has_access(self, user_id: int, chat_id: int) -> bool:
        """Проверка доступа пользователя к чату."""
        return await self.chat_repo.user_has_access(user_id, chat_id)
