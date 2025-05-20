"""
Базовые схемы данных для приложения.
Содержит общие классы и утилиты для работы с Pydantic моделями.
Определяет базовые классы для всех схем данных в приложении.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    """Базовая схема с общими полями."""

    class Config:  # noqa: D106
        from_attributes = True  # Для совместимости с ORM


class TimestampSchema(BaseSchema):
    """Схема с временными метками."""

    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime | None = Field(None, description="Дата обновления")
