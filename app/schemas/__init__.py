"""
Пакет схем данных приложения.
Содержит все Pydantic модели для валидации и сериализации данных.
Обеспечивает типизацию и документацию API.
"""

from .base import BaseSchema, TimestampSchema
from .chat import ChatBase, ChatCreate, ChatRead
from .group import GroupBase, GroupCreate, GroupRead
from .message import MessageBase, MessageCreate, MessageRead
from .token import Token, TokenData
from .user import UserBase, UserCreate, UserRead

__all__ = [
    'BaseSchema',
    'TimestampSchema',
    'ChatBase',
    'ChatCreate',
    'ChatRead',
    'UserBase',
    'GroupBase',
    'GroupCreate',
    'GroupRead',
    'MessageBase',
    'MessageCreate',
    'MessageRead',
    'Token',
    'TokenData',
    'UserCreate',
    'UserRead',
]
