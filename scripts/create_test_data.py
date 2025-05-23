"""Скрипт для создания тестовых данных."""
import asyncio
import sys
from pathlib import Path

from app.db.models import Chat, Group, Message, User, UserChat
from app.db.session import write_session
from app.services.auth import get_password_hash

project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)


async def create_test_data():
    """Создание тестовых данных."""
    async with write_session() as session:
        # Создание пользователей
        users = []
        for i in range(1, 6):  # 5 пользователей
            user = User(
                username=f"user{i}",
                email=f"user{i}@example.com",
                hashed_password=get_password_hash("password123"),
            )
            session.add(user)
            users.append(user)
        await session.commit()

        print("\nСозданные пользователи:")
        for user in users:
            print(f"- {user.username} (ID: {user.id})")

        # Создание личных чатов между пользователями
        personal_chats = []
        for i in range(1, 5):
            chat = Chat(
                name=f"Личный чат {i}-{i+1}",
                is_group=False
            )
            session.add(chat)
            await session.commit()
            personal_chats.append(chat)

            # Добавление пользователей в чат
            user_chat1 = UserChat(user_id=i, chat_id=chat.id)
            user_chat2 = UserChat(user_id=i+1, chat_id=chat.id)
            session.add_all([user_chat1, user_chat2])
            await session.commit()

            # Добавление нескольких сообщений в каждый чат
            messages = []
            for j in range(3):
                message = Message(
                    chat_id=chat.id,
                    sender_id=i if j % 2 == 0 else i+1,
                    text=f"Тестовое сообщение {j+1} в чате {chat.id}"
                )
                session.add(message)
                messages.append(message)
            await session.commit()

        print("\nСозданные личные чаты:")
        for chat in personal_chats:
            print(f"- Чат '{chat.name}' (ID: {chat.id})")

        # Создание группового чата
        group_chat = Chat(
            name="Тестовая группа",
            is_group=True
        )
        session.add(group_chat)
        await session.commit()

        # Создание группы
        group = Group(
            chat_id=group_chat.id,
            name="Тестовая группа",
            creator_id=1,
            members=[1, 2, 3, 4, 5]  # Все пользователи в группе
        )
        session.add(group)
        await session.commit()

        # Добавление сообщений в групповой чат
        group_messages = []
        for i in range(1, 6):
            message = Message(
                chat_id=group_chat.id,
                sender_id=i,
                text=f"Сообщение в группе от пользователя {i}"
            )
            session.add(message)
            group_messages.append(message)
        await session.commit()

        print("\nСозданный групповой чат:")
        print(f"- Группа '{group_chat.name}' (ID: {group_chat.id})")
        print(f"  Участники: {', '.join(str(m) for m in group.members)}")

        print("\nТестовые данные успешно созданы")
        print("\nДля тестирования приложения используйте следующие учетные данные:")
        print("Логин: user1")
        print("Пароль: password123")


if __name__ == "__main__":
    asyncio.run(create_test_data())
