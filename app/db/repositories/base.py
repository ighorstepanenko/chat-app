"""
Базовый репозиторий для работы с моделями базы данных.
Предоставляет общие методы CRUD операций и базовую функциональность для всех репозиториев.
Реализует паттерн Repository для абстракции доступа к данным.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Базовый класс репозитория с общими методами для работы с моделями."""

    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, instance_id: int) -> ModelType | None:
        """Получение записи по ID."""
        result = await self.session.execute(
            select(self.model).where(self.model.id == instance_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[ModelType]:
        """Получение всех записей."""
        result = await self.session.execute(select(self.model))
        return list(result.scalars().all())

    async def create(self, data: dict[str, Any]) -> ModelType:
        """Создание новой записи."""
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update(self, instance_id: int, data: dict[str, Any]) -> ModelType | None:
        """Обновление записи."""
        instance = await self.get(instance_id)
        if instance:
            for key, value in data.items():
                setattr(instance, key, value)
            await self.session.commit()
            await self.session.refresh(instance)
        return instance

    async def delete(self, instance_id: int) -> bool:
        """Удаление записи."""
        instance = await self.get(instance_id)
        if instance:
            await self.session.delete(instance)
            await self.session.commit()
            return True
        return False

    async def count(self) -> int:
        """Подсчет количества объектов."""
        result = await self.session.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()
