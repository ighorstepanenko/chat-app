from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.schemas import TokenData

# Настройки для хеширования паролей
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет соответствие пароля и его хеша.

    Args:
        plain_password: Пароль в чистом виде
        hashed_password: Хешированный пароль

    Returns:
        bool: True если пароль верный, иначе False

    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Генерирует хеш пароля.

    Args:
        password: Пароль в чистом виде

    Returns:
        str: Хешированный пароль

    """
    return pwd_context.hash(password)


def create_access_token(token_data: TokenData) -> str:
    """
    Создает JWT токен на основе структурированных данных.

    Args:
        token_data: Данные для кодирования в токене

    Returns:
        str: JWT токен

    """
    to_encode = token_data.dict()
    expire = datetime.now(UTC) + timedelta(minutes=settings.auth.access_token_expire_minutes)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, settings.auth.secret_key, algorithm=settings.auth.token_algorythm)


def decode_token(token: str) -> dict | None:
    """
    Декодирует JWT токен.

    Args:
        token: JWT токен

    Returns:
        dict: Декодированные данные или None, если токен невалидный

    """
    try:
        return jwt.decode(token, settings.auth.secret_key, algorithms=[settings.auth.token_algorythm])
    except JWTError:
        return None
