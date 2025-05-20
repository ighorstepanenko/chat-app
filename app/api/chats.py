"""
Модуль управления чатами.
Содержит ручки для создания личных и групповых чатов.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_chat_service, get_current_user
from app.schemas.chat import ChatCreate, ChatRead
from app.services.chat import ChatService

router = APIRouter(prefix='/chats', tags=['chats'])


@router.post('/', response_model=ChatRead, status_code=status.HTTP_201_CREATED)
async def create_chat(
        chat_data: ChatCreate,
        current_user_id: int = Depends(get_current_user),
        service: ChatService = Depends(get_chat_service)
):
    """
    Создание нового чата.

    Параметры:
    - name: название чата
    - is_group: флаг группового чата
    - user_id: ID пользователя для личного чата

    Возвращает:
    - Созданный чат с ID и метаданными
    """
    try:
        chat_data.current_user_id = current_user_id
        return await service.create_chat(chat_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
