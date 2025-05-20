"""
Схемы данных для работы с токенами аутентификации.
Содержит модели для создания и валидации токенов доступа.
Определяет структуру данных для JWT токенов.
"""
from pydantic import BaseModel


class Token(BaseModel):
    """Схема для JWT токена."""

    access_token: str


class TokenData(BaseModel):
    """Схема с данными в токене."""

    user_id: str
