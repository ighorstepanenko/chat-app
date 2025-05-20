from .auth import router as auth_router
from .chats import router as chats_router
from .groups import router as groups_router
from .messages import router as messages_router
from .websocket import router as websocket_router

__all__ = ('auth_router', 'chats_router', 'groups_router', 'messages_router', 'websocket_router')
