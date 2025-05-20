"""
Основной модуль приложения FastAPI.
Инициализирует и настраивает приложение, подключает все роутеры и middleware.
Содержит конфигурацию CORS и настройки для WebSocket соединений.
"""
import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth_router, chats_router, groups_router, messages_router, websocket_router
from app.core.dependencies import get_current_user
from app.logger import setup_logger


def create_app() -> FastAPI:
    """Инициализация приложения."""
    app = FastAPI()

    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # В продакшене заменить на конкретные домены
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    setup_routers(app)
    setup_logger()

    return app


def setup_routers(app: FastAPI) -> None:
    """Установка маршрутизации приложения."""
    app.include_router(auth_router, prefix='/api/v1')
    app.include_router(chats_router, prefix='/api/v1')
    app.include_router(groups_router, prefix='/api/v1')
    app.include_router(messages_router, prefix='/api/v1')
    app.include_router(websocket_router)


app = create_app()

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
