# Chat Application

Веб-приложение для обмена сообщениями с поддержкой личных и групповых чатов, реализованное на FastAPI с использованием WebSocket для real-time коммуникации.

## Используемые технологии

- Python 3.12+
- FastAPI
- SQLAlchemy (асинхронный режим)
- PostgreSQL
- WebSocket
- Docker & Docker Compose
- PDM (менеджер зависимостей)

## Запуск проекта

### Требования

- Docker
- Docker Compose

### Шаги для запуска

1. Клонируйте репозиторий:
```bash
git clone https://github.com/ighorstepanenko/chat-app.git
cd chat-app
```

2. Создайте файл `.env` в корневой директории:
```bash
DATABASE_DSN=postgresql+asyncpg://postgres:postgres@db:5432/chat_db
SECRET_KEY=your-secret-key-here
```

3. Запустите проект через Docker Compose:
```bash
docker compose up --build
```

4. В отдельном терминале примените миграции:
```bash
docker compose exec backend alembic upgrade head
```

5. Создайте тестовые данные:
```bash
docker compose exec backend python scripts/create_test_data.py
```

Приложение будет доступно по адресу: http://localhost:8000

API документация доступна по адресу: http://localhost:8000/docs

## Тестовые данные

После запуска скрипта `create_test_data.py` будут созданы:

- 5 пользователей (user1-user5) с паролем "password123"
- 4 личных чата между последовательными пользователями
- 1 групповой чат со всеми пользователями
- Тестовые сообщения в каждом чате

Вы можете использовать следующие учетные данные для тестирования:
- Username: user1
- Password: password123

## API Endpoints

### Аутентификация

#### Регистрация пользователя
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user6",
    "email": "user6@example.com",
    "password": "password123"
  }'
```

#### Получение токена доступа
```bash
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user1&password=password123"
```

### Чаты

#### Создание личного чата
```bash
curl -X POST http://localhost:8000/api/v1/chats/ \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 3
  }'
```

#### Создание группового чата
```bash
curl -X POST http://localhost:8000/api/v1/groups/ \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Group",
  }'
```

### Сообщения

#### Отправка сообщения
```bash
curl -X POST http://localhost:8000/api/v1/messages/{chat_id}/send \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, world!"
  }'
```

#### Получение истории сообщений
```bash
curl -X GET "http://localhost:8000/api/v1/messages/history/{chat_id}?limit=100&offset=0" \
  -H "Authorization: Bearer <your-token>"
```

### WebSocket

#### Подключение к WebSocket

Для подключения к WebSocket используйте следующий URL:
```
ws://localhost:8000/ws/{chat_id}?token=<your-token>
```

#### Тестирование WebSocket

1. Получите токен доступа:
```bash
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user1&password=password123"
```

2. Получите список сообщений чата, чтобы узнать их ID:
```bash
curl -X GET "http://localhost:8000/api/v1/messages/history/5?limit=100&offset=0" \
  -H "Authorization: Bearer <your-token>"
```

3. Откройте файл `scripts/test_websocket.html` в браузере и замените `YOUR_TOKEN` на полученный токен.

4. В открывшемся интерфейсе:
   - Введите ID сообщения, которое хотите пометить как прочитанное
   - Нажмите кнопку "Mark as Read"
   - В окне сообщений вы увидите уведомления о статусе прочтения

5. Для тестирования взаимодействия между пользователями:
   - Откройте `test_websocket.html` в двух разных вкладках браузера
   - Используйте разные токены для разных пользователей
   - Пометьте сообщение как прочитанное в одной вкладке
   - В другой вкладке вы увидите уведомление о прочтении

#### Форматы сообщений WebSocket

Отправка сообщения:
```json
{
  "type": "message",
  "text": "Hello via WebSocket!"
}
```

Пометка сообщения как прочитанного:
```json
{
  "type": "read",
  "message_id": 123
}
```

Получение уведомления о прочтении:
```json
{
  "type": "read",
  "message_id": 123,
  "chat_id": 5,
  "reader_id": 1
}
```

## Структура проекта

```
chat-app/
├── app/
│   ├── api/            # API endpoints
│   ├── core/           # Core functionality
│   ├── db/             # Database models and repositories
│   ├── schemas/        # Pydantic models
│   ├── services/       # Business logic
│   └── websocket/      # WebSocket implementation
├── migrations/         # Alembic migrations
├── docker-compose.yaml # Docker configuration
├── Dockerfile         # Docker build instructions
└── pyproject.toml     # Project dependencies
```

## Разработка

### Установка зависимостей

```bash
pdm install
```

### Запуск миграций

```bash
alembic upgrade head
```

### Запуск в режиме разработки

```bash
uvicorn app.main:app --reload
```
