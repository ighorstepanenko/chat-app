"""
Сервис для работы с чатами.
Содержит бизнес-логику для создания и управления чатами.
Реализует проверку прав доступа и управление участниками чатов.
"""
from app.db.repositories.chat import ChatRepository
from app.schemas.chat import ChatCreate, ChatRead


class ChatService:
    """Сервис для работы с чатами."""

    def __init__(self, chat_repo: ChatRepository):
        self.chat_repo = chat_repo

    async def create_chat(self, chat_data: ChatCreate) -> ChatRead:
        """
        Создание нового чата.

        Args:
            chat_data: Данные для создания чата

        Returns:
            ChatRead: Созданный чат

        """
        # Проверка существования личного чата между пользователями
        if await self.chat_repo.check_chat_exists(chat_data.current_user_id, chat_data.user_id):
            msg = 'Личный чат между этими пользователями уже существует'
            raise ValueError(msg)

        # Для личного чата генерируем имя на основе ID пользователей
        if not chat_data.is_group:
            chat_data.name = f"Personal Chat {chat_data.user_id}"

        chat = await self.chat_repo.create({
            "name": chat_data.name,
            "is_group": chat_data.is_group
        })

        # Добавляем обоих пользователей в чат
        await self.chat_repo.add_user_to_chat(chat.id, chat_data.current_user_id)
        await self.chat_repo.add_user_to_chat(chat.id, chat_data.user_id)

        return ChatRead.from_orm(chat)
