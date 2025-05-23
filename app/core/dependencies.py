"""Модуль зависимостей приложения."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.repositories.chat import ChatRepository
from app.db.repositories.group import GroupRepository
from app.db.repositories.message import MessageRepository
from app.db.repositories.user import UserRepository
from app.db.session import get_db
from app.services import ChatService, GroupService, MessageService, UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/v1/auth/token')


async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Зависимость для получения сервиса работы с пользователями."""
    return UserService(UserRepository(db))


async def get_chat_service(db: AsyncSession = Depends(get_db)) -> ChatService:
    """Зависимость для получения сервиса чатов."""
    return ChatService(ChatRepository(db))


async def get_group_service(db: AsyncSession = Depends(get_db)) -> GroupService:
    """Зависимость для получения сервиса групп."""
    return GroupService(GroupRepository(db), ChatRepository(db))


async def get_message_service(db: AsyncSession = Depends(get_db)) -> MessageService:
    """Зависимость для получения сервиса сообщений."""
    return MessageService(MessageRepository(db), ChatRepository(db))


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> int:
    """
    Авторизация пользователя.

    Args:
        token: JWT токен
        db: Сессия базы данных

    Returns:
        int: ID пользователя

    """
    try:
        payload = jwt.decode(token, settings.auth.secret_key, algorithms=[settings.auth.token_algorythm])
        user_id: int = int(payload.get('user_id')) if payload.get('user_id') is not None else None
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Токен не содержит ID пользователя'
            )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Недействительный токен'
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Некорректный формат ID пользователя в токене'
        ) from e

    # Проверка существования пользователя
    repo = UserRepository(db)
    if not await repo.get(user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Пользователь не найден в БД'
        )

    return user_id
