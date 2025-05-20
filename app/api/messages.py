"""
Модуль управления сообщениями.
Содержит ручки для отправки сообщений и получения истории сообщений.
Реализует пагинацию и фильтрацию сообщений по чатам.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user, get_message_service
from app.schemas.message import MessageCreate, MessageRead
from app.services.message import MessageService

router = APIRouter(prefix='/messages', tags=['messages'])


@router.post('/{chat_id}/send', response_model=MessageRead, status_code=status.HTTP_201_CREATED)
async def send_message(
        chat_id: int,
        message_data: MessageCreate,
        current_user: int = Depends(get_current_user),
        service: MessageService = Depends(get_message_service)
):
    """
    Отправка сообщения в чат.

    Параметры:
    - chat_id: ID чата
    - text: текст сообщения

    Возвращает:
    - Отправленное сообщение с ID и временем отправки
    """
    try:
        return await service.send_message(
            chat_id=chat_id,
            sender_id=current_user,
            text=message_data.text
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e


@router.get('/history/{chat_id}', response_model=list[MessageRead])
async def get_chat_history(
        chat_id: int,
        current_user: int = Depends(get_current_user),
        service: MessageService = Depends(get_message_service),
        limit: int = 100,
        offset: int = 0,
):
    """
    Получение истории сообщений чата.

    Параметры:
    - chat_id: ID чата
    - limit: количество сообщений (по умолчанию 100)
    - offset: смещение (для пагинации)

    Возвращает:
    - Список сообщений в хронологическом порядке
    """
    try:
        return await service.get_chat_history(chat_id, current_user, limit, offset)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e
