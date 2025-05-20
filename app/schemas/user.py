"""
Схемы данных для работы с пользователями.
Содержит модели для создания, обновления и чтения данных пользователей.
Определяет структуру данных для аутентификации и профилей пользователей.
"""
from pydantic import BaseModel, EmailStr, Field

from .base import BaseSchema


class UserBase(BaseModel):
    """Базовая схема пользователя."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., example="user@example.com")


class UserCreate(UserBase):
    """Схема для создания пользователя."""

    password: str = Field(..., min_length=6, example="strongpassword")


class UserRead(UserBase, BaseSchema):
    """Схема для чтения данных пользователя."""

    id: int = Field(..., description="ID пользователя")
