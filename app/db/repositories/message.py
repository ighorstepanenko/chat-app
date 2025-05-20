"""
Репозиторий для работы с сообщениями в базе данных.
Содержит методы для создания, получения и обновления сообщений.
Реализует функционал пометки сообщений как прочитанных и получения истории сообщений.
"""
from sqlalchemy import Sequence, desc, select, update

from app.db.models import Message
from app.db.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    """Репозиторий для работы с сообщениями."""

    def __init__(self, session):
        super().__init__(Message, session)

    async def get_chat_messages(self, chat_id: int, limit: int = 100, offset: int = 0) -> Sequence[Message]:
        """Получение сообщений чата с пагинацией."""
        result = await self.session.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def mark_as_read(self, message_id: int) -> bool:
        """Пометка сообщения как прочитанного."""
        result = await self.session.execute(
            update(Message)
            .where(Message.id == message_id)
            .values(is_read=True)
            .returning(Message.id)
        )
        await self.session.commit()
        return result.scalar_one_or_none() is not None
