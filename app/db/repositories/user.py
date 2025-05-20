"""
Репозиторий для работы с пользователями в базе данных.
Содержит методы для получения пользователей.
"""

from sqlalchemy import select

from app.db.models import User
from app.db.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Репозиторий для работы с пользователями."""

    def __init__(self, session):
        super().__init__(User, session)

    async def get_by_username(self, username: str) -> User | None:
        """Получение пользователя по username."""
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Получение пользователя по email."""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
