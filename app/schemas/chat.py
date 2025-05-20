"""
Схемы данных для работы с чатами.
Содержит модели для создания, обновления и чтения данных чатов.
Определяет структуру данных для личных и групповых чатов.
"""

from pydantic import BaseModel, Field

from .base import BaseSchema


class ChatBase(BaseModel):
    """Базовая схема чата."""

    name: str | None = Field(None, max_length=100, example="Мой чат")
    is_group: bool = Field(False, description="Флаг группового чата")


class ChatCreate(ChatBase):
    """Схема для создания чата."""

    user_id: int = Field(..., description="ID пользователя для личного чата")
    current_user_id: int | None = Field(None, description="ID текущего пользователя (заполняется автоматически)")


class ChatRead(ChatBase, BaseSchema):
    """Схема для чтения данных чата."""

    id: int = Field(..., description="ID чата")
