"""
Менеджер WebSocket соединений.
Управляет активными WebSocket соединениями и их жизненным циклом.
Обрабатывает подключение/отключение пользователей и маршрутизацию сообщений.
"""

import json

from fastapi import WebSocket

from app.core.security import decode_token
from app.services.message import MessageService


class ConnectionManager:
    """
    Менеджер для управления WebSocket соединениями и рассылкой сообщений.

    Атрибуты:
        active_connections: Словарь активных соединений {user_id: websocket}
        user_chats: Словарь чатов пользователей {user_id: set(chat_ids)}
        chat_users: Словарь пользователей в чатах {chat_id: set(user_ids)}
    """

    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}
        self.user_chats: dict[int, set[int]] = {}
        self.chat_users: dict[int, set[int]] = {}

    async def authenticate_token(self, token: str) -> int:
        """
        Аутентификация пользователя по JWT токену.

        Args:
            token: JWT токен

        Returns:
            int: ID пользователя

        Raises:
            ValueError: Если токен невалидный

        """
        payload = decode_token(token)
        if not payload or 'user_id' not in payload:
            msg = 'Invalid token'
            raise ValueError(msg)
        return int(payload['user_id'])

    async def connect(self, user_id: int, chat_id: int, websocket: WebSocket):
        """
        Регистрирует новое подключение пользователя к чату.

        Args:
            user_id: ID пользователя
            chat_id: ID чата
            websocket: Объект WebSocket соединения

        """
        await websocket.accept()

        self.active_connections[user_id] = websocket

        if user_id not in self.user_chats:
            self.user_chats[user_id] = set()
        self.user_chats[user_id].add(chat_id)

        if chat_id not in self.chat_users:
            self.chat_users[chat_id] = set()
        self.chat_users[chat_id].add(user_id)

    def disconnect(self, user_id: int, chat_id: int):
        """
        Удаляет подключение пользователя.

        Args:
            user_id: ID пользователя
            chat_id: ID чата

        """
        if user_id in self.active_connections:
            del self.active_connections[user_id]

        if user_id in self.user_chats and chat_id in self.user_chats[user_id]:
            self.user_chats[user_id].remove(chat_id)

        if chat_id in self.chat_users and user_id in self.chat_users[chat_id]:
            self.chat_users[chat_id].remove(user_id)

    async def send_personal_message(self, message: str, user_id: int):
        """
        Отправляет сообщение конкретному пользователю.

        Args:
            message: Текст сообщения
            user_id: ID пользователя-получателя

        """
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

    async def broadcast_to_chat(self, message: str, chat_id: int, exclude_user: int | None = None):
        """
        Рассылает сообщение всем участникам чата.

        Args:
            message: Текст сообщения
            chat_id: ID чата
            exclude_user: ID пользователя, которому не нужно отправлять сообщение

        """
        if chat_id not in self.chat_users:
            return

        for user_id in self.chat_users[chat_id]:
            if user_id != exclude_user and user_id in self.active_connections:
                await self.active_connections[user_id].send_text(message)

    async def handle_message(self, user_id: int, chat_id: int, data: str, message_service: MessageService):
        """
        Обрабатывает входящее сообщение через WebSocket.

        Args:
            user_id: ID отправителя
            chat_id: ID чата
            data: Строка с данными сообщения
            message_service: Сервис для работы с сообщениями

        """
        try:
            message_data = json.loads(data)

            if message_data.get('type') == 'message':
                # Создание нового сообщения
                message = await message_service.send_message(
                    chat_id=chat_id,
                    sender_id=user_id,
                    text=message_data['text']
                )

                # Рассылка сообщения участникам чата
                await self.broadcast_to_chat(
                    json.dumps({
                        'type': 'message',
                        'id': message.id,
                        'text': message.text,
                        'sender_id': user_id,
                        'timestamp': message.created_at.isoformat()
                    }),
                    chat_id,
                    exclude_user=user_id
                )

            elif message_data.get('type') == 'read':
                # Пометка сообщения как прочитанного
                message_id = message_data['message_id']
                await message_service.mark_as_read(message_id)

                # Уведомление участников чата
                await self.broadcast_to_chat(
                    json.dumps({
                        'type': 'read',
                        'message_id': message_id,
                        'chat_id': chat_id,
                        'reader_id': user_id
                    }),
                    chat_id,
                    exclude_user=user_id
                )

        except (json.JSONDecodeError, KeyError, ValueError):
            await self.send_personal_message(
                json.dumps({'error': 'Invalid message format'}),
                user_id
            )
