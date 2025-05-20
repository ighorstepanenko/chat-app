"""
Схемы данных для работы с групповыми чатами.
Содержит модели для создания, обновления и чтения данных групп.
Определяет структуру данных для управления участниками групп.
"""

from pydantic import BaseModel, Field

from .base import BaseSchema


class GroupBase(BaseModel):
    """Базовая схема группы."""

    name: str = Field(..., max_length=100, example="Моя группа")
    creator_id: int = Field(..., description="ID создателя группы")


class GroupCreate(GroupBase):
    """Схема для создания группы."""


class GroupRead(BaseSchema):
    """Схема для чтения данных группы."""

    id: int = Field(..., description="ID группы")
    creator_id: int = Field(..., description="ID создателя группы")
    members: list[int] = Field(..., description="Список ID участников")


class GroupInfo(BaseSchema):
    """Схема для отображения группы."""

    id: int = Field(..., description="ID группы")
    name: str = Field(..., description="Название группы")
    creator_id: int = Field(..., description="ID создателя группы")
    members: list[int] = Field(..., description="Список ID участников")


class GroupList(BaseSchema):
    """Схема для отображения списка групп."""

    groups: list[GroupInfo]
