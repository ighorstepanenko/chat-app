"""Описание моделей базы данных."""

import datetime
from typing import ClassVar

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class User(Base):
    """Модель пользователя."""

    __tablename__ = 'users'
    __table_args__: ClassVar[dict[str, str]] = {'comment': 'Пользователи системы'}

    id: Mapped[int] = mapped_column(
        sa.Identity(always=True),
        primary_key=True,
        index=True,
        comment='Уникальный идентификатор пользователя'
    )
    username: Mapped[str] = mapped_column(sa.String(50), unique=True, index=True, comment='Username пользователя')
    email: Mapped[str] = mapped_column(sa.String(100), unique=True, index=True, comment='Email пользователя')
    hashed_password: Mapped[str] = mapped_column(sa.String(255), comment='Хэшированный пароль')
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        comment='Дата регистрации'
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
        comment='Дата последнего обновления'
    )


class Chat(Base):
    """Модель чата."""

    __tablename__ = 'chats'
    __table_args__: ClassVar[dict[str, str]] = {'comment': 'Чаты пользователей'}

    id: Mapped[int] = mapped_column(
        sa.Identity(always=True),
        primary_key=True,
        index=True,
        comment='Уникальный идентификатор чата'
    )
    name: Mapped[str] = mapped_column(sa.String(100), comment='Название чата')
    is_group: Mapped[bool] = mapped_column(
        server_default=sa.false(),
        comment='Флаг группового чата (True - группа, False - личный)'
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        comment='Дата создания чата'
    )


class UserChat(Base):
    """Ассоциативная таблица пользователей и чатов (для личных чатов)."""

    __tablename__ = 'user_chats'
    __table_args__: ClassVar[dict[str, str]] = {'comment': 'Связь пользователей с чатами'}

    id: Mapped[int] = mapped_column(
        sa.Identity(always=True),
        primary_key=True,
        comment='Уникальный идентификатор связи'
    )
    user_id: Mapped[int] = mapped_column(sa.ForeignKey('users.id'), index=True, comment='ID пользователя')
    chat_id: Mapped[int] = mapped_column(sa.ForeignKey('chats.id'), index=True, comment='ID чата')
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        comment='Дата создания связи'
    )


class Group(Base):
    """Модель группового чата."""

    __tablename__ = 'groups'
    __table_args__: ClassVar[dict[str, str]] = {'comment': 'Групповые чаты'}

    id: Mapped[int] = mapped_column(
        sa.Identity(always=True),
        primary_key=True,
        index=True,
        comment='Уникальный идентификатор группы'
    )
    chat_id: Mapped[int] = mapped_column(sa.ForeignKey('chats.id'), unique=True, comment='ID связанного чата')
    name: Mapped[str] = mapped_column(sa.String(100), comment='Название группы')
    creator_id: Mapped[int] = mapped_column(sa.ForeignKey('users.id'), comment='ID создателя группы')
    members: Mapped[list[int]] = mapped_column(sa.JSON, comment='Список ID участников группы')
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        comment='Дата создания группы'
    )


class Message(Base):
    """Модель сообщения."""

    __tablename__ = 'messages'
    __table_args__: ClassVar[dict[str, str]] = {'comment': 'Сообщения в чатах'}

    id: Mapped[int] = mapped_column(
        sa.Identity(always=True),
        primary_key=True,
        index=True,
        comment='Уникальный идентификатор сообщения'
    )
    chat_id: Mapped[int] = mapped_column(sa.ForeignKey('chats.id'), index=True, comment='ID чата')
    sender_id: Mapped[int] = mapped_column(sa.ForeignKey('users.id'), comment='ID отправителя')
    text: Mapped[str] = mapped_column(sa.Text(), comment='Текст сообщения')
    is_read: Mapped[bool] = mapped_column(server_default=sa.false(), comment='Флаг прочитанного сообщения')
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        comment='Дата и время отправки'
    )
