"""
Сервис аутентификации и авторизации.
Содержит логику для регистрации, аутентификации и управления пользователями.
Реализует JWT-токены для безопасной аутентификации.
"""
from passlib.context import CryptContext

from app.db.repositories.user import UserRepository
from app.schemas.user import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка соответствия пароля хешу."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Генерация хеша пароля."""
    return pwd_context.hash(password)


class UserService:
    """Сервис для работы с аутентификацией и пользователями."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def create_user(self, user_data: UserCreate):
        """
        Создание нового пользователя.

        Args:
            user_data: Данные для создания пользователя

        Returns:
            User: Созданный пользователь

        """
        if await self.user_repo.get_by_username(user_data.username):
            msg = "Пользователь с таким username уже существует"
            raise ValueError(msg)

        if await self.user_repo.get_by_email(user_data.email):
            msg = "Пользователь с таким email уже существует"
            raise ValueError(msg)

        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
        return await self.user_repo.create(user_dict)

    async def authenticate_user(self, username: str, password: str):
        """
        Аутентификация пользователя.

        Args:
            username: Логин пользователя
            password: Пароль пользователя

        Returns:
            User: Объект пользователя или None если аутентификация не удалась

        """
        user = await self.user_repo.get_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
