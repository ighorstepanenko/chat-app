"""
Схемы данных для работы с сообщениями.
Содержит модели для создания, обновления и чтения данных сообщений.
Определяет структуру данных для текстовых сообщений в чатах.
"""
from datetime import datetime

from pydantic import BaseModel, Field

from .base import BaseSchema


class MessageBase(BaseModel):
    """Базовая схема сообщения."""

    text: str = Field(..., description="Текст сообщения")


class MessageCreate(MessageBase):
    """Схема для создания сообщения."""


class MessageRead(MessageBase, BaseSchema):
    """Схема для чтения данных сообщения."""

    id: int = Field(..., description="ID сообщения")
    chat_id: int = Field(..., description="ID чата")
    sender_id: int = Field(..., description="ID отправителя")
    is_read: bool = Field(False, description="Флаг прочитанного сообщения")
    created_at: datetime = Field(..., description="Дата и время отправки")
