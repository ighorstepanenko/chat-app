"""
Модуль управления чатами.
Содержит ручки для создания личных и групповых чатов.
"""

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_chat_service
from app.schemas.chat import ChatCreate, ChatRead
from app.services.chat import ChatService

router = APIRouter(prefix='/chats', tags=['chats'])


@router.post('/', response_model=ChatRead, status_code=status.HTTP_201_CREATED)
async def create_chat(
        chat_data: ChatCreate,
        service: ChatService = Depends(get_chat_service)
):
    """
    Создание нового чата.

    Параметры:
    - name: название чата
    - is_group: флаг группового чата

    Возвращает:
    - Созданный чат с ID и метаданными
    """
    return await service.create_chat(chat_data)
