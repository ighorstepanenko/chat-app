"""
Сервис для работы с чатами.
Содержит бизнес-логику для создания и управления чатами.
Реализует проверку прав доступа и управление участниками чатов.
"""
from app.db.repositories.chat import ChatRepository
from app.db.repositories.group import GroupRepository
from app.schemas.chat import ChatCreate, ChatRead
from app.schemas.group import GroupCreate, GroupRead


class ChatService:
    """Сервис для работы с чатами."""

    def __init__(self, chat_repo: ChatRepository, group_repo: GroupRepository):
        self.chat_repo = chat_repo
        self.group_repo = group_repo

    async def create_chat(self, chat_data: ChatCreate) -> ChatRead:
        """
        Создание нового чата.

        Args:
            chat_data: Данные для создания чата

        Returns:
            ChatRead: Созданный чат

        """
        # Для личного чата генерируем имя на основе ID пользователей
        if not chat_data.is_group:
            chat_data.name = f"Personal Chat {chat_data.user_id}"

        chat = await self.chat_repo.create({
            "name": chat_data.name,
            "is_group": chat_data.is_group
        })

        # Для личного чата создаем связь с пользователем
        if not chat_data.is_group:
            await self.chat_repo.add_user_to_chat(chat.id, chat_data.user_id)

        return ChatRead.from_orm(chat)
