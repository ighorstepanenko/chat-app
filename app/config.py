"""Основные настройки приложения."""

import logging

from pydantic_settings import BaseSettings


class LoggerSettings(BaseSettings):
    """Конфигурирование логгирования приложения."""

    environment: str = 'local'
    logger_level: int = logging.INFO


class DataBaseSettings(BaseSettings):
    """Настройки подключенияк БД."""

    database_dsn: str


class AuthSettings(BaseSettings):
    """Настройки аутентификации."""

    secret_key: str
    token_algorythm: str = 'HS256'
    access_token_expire_minutes: int = 30


class Settings(BaseSettings):
    """Общие настройки приложения."""

    logger: LoggerSettings
    database: DataBaseSettings
    auth: AuthSettings


settings: Settings = Settings(logger=LoggerSettings(), database=DataBaseSettings(), auth=AuthSettings())
