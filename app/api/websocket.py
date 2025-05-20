"""
Модуль WebSocket соединений.
Реализует real-time коммуникацию между пользователями через WebSocket.
Обрабатывает подключения, аутентификацию и маршрутизацию сообщений.
"""

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.dependencies import get_message_service
from app.db.repositories.chat import ChatRepository
from app.db.session import get_db
from app.websocket.manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()


@router.websocket('/ws/{chat_id}')
async def websocket_endpoint(
        websocket: WebSocket,
        chat_id: int,
        token: str,
        db: AsyncSession = Depends(get_db)
):
    """
    WebSocket соединение для реального времени.

    Параметры:
    - chat_id: ID чата
    - token: JWT токен для аутентификации

    Функционал:
    - Отправка/получение сообщений в реальном времени
    - Обновление статусов прочтения
    """
    try:
        # Аутентификация через токен
        user_id = await manager.authenticate_token(token)

        # Проверка доступа к чату
        chat_repo = ChatRepository(db)
        if not await chat_repo.user_has_access(user_id, chat_id):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Подключение
        await manager.connect(user_id, chat_id, websocket)

        try:
            message_service = await get_message_service()
            while True:
                data = await websocket.receive_text()
                await manager.handle_message(user_id, chat_id, data, message_service)
        except WebSocketDisconnect:
            manager.disconnect(user_id, chat_id)
    except Exception:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
