# Бэкенд Healthity

Сервис на FastAPI, отвечающий за хранение пользователей Telegram, управление персонажами, предметами, активностями и работу бизнес-логики через use-case-слой. В качестве хранилищ используются PostgreSQL и Redis, взаимодействие организовано через асинхронные репозитории и контейнер зависимостей.

## 📖 Документация API

Полная документация API доступна в файле [API_DOCUMENTATION.md](src/drivers/rest/API_DOCUMENTATION.md).

**Интерактивная документация:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

**Основные endpoints:**
- 🔐 Аутентификация: `/api/v1/auth/*`
- 👤 Пользователи: `/api/v1/users/*`
- 🎮 Персонажи: `/api/v1/characters/*`
- 🛍️ Каталоги (открытые): `/api/v1/{items,backgrounds,activity-types}/catalog`
- 💰 Покупки: `/api/v1/character-{items,backgrounds}/purchase`
- 📊 Активности: `/api/v1/daily-activities/*`
- 😊 Настроение: `/api/v1/mood-history/*`
- 👥 Друзья: `/api/v1/user-friends/*`

## 🛠️ Стек технологий

- **Python 3.13**, FastAPI, Starlette
- **SQLAlchemy 2** с асинхронным движком и миграциями Alembic
- **PostgreSQL** (через asyncpg), **Redis** и **RabbitMQ**
- **Dependency Injector** для управления зависимостями
- **JWT** для аутентификации пользователей
- **Pydantic** для валидации данных
- **Docker Compose** для локальной инфраструктуры
- **Poetry** для управления зависимостями

## 📁 Структура проекта

Проект следует принципам **Clean Architecture** и **Domain-Driven Design**:

```
src/
  adapters/              # Адаптеры внешних систем
    database/            # Модели SQLAlchemy, сессии, миграции
    repositories/        # Реализации репозиториев (SQLAlchemy)
  core/                  # Ядро приложения
    auth/                # JWT сервис, провайдеры токенов
    settings.py          # Конфигурация на базе Pydantic
    security.py          # Хеширование паролей
  domain/                # Доменный слой
    entities/            # Доменные сущности (User, Character, Item, etc.)
    value_objects/       # Value Objects (TelegramId, Coin, Experience)
    exceptions.py        # Доменные исключения
  drivers/rest/          # REST API транспортный слой
    schemas/             # Pydantic схемы для API
    *.py                 # Роуты FastAPI
  ports/                 # Порты (интерфейсы репозиториев)
    repositories/        # Абстрактные классы репозиториев
  use_cases/             # Бизнес-логика (Use Cases)
    users/               # Use cases для пользователей
    characters/          # Use cases для персонажей
    daily_activities/    # Use cases для активностей
    mood_history/        # Use cases для настроения
    transactions/        # Use cases для транзакций
    ...
  app.py                 # Точка входа FastAPI с lifespan-хуками
  container.py           # Dependency Injector контейнер
```

### Основные принципы архитектуры:

- **Dependency Injection**: Все зависимости инжектируются через DI контейнер
- **Repository Pattern**: Доступ к данным через абстрактные репозитории
- **Use Case Pattern**: Бизнес-логика изолирована в use cases
- **Domain Entities**: Чистые доменные сущности без зависимостей от фреймворков
- **DTO/Schemas**: Pydantic схемы для валидации и сериализации данных

## Запуск проекта

### 1. Настройка окружения

При необходимости создайте или обновите файл `.env`:

```bash
cp .env.example .env  # если примера нет, создайте .env вручную
```

Ключевые переменные окружения:

### База данных (PostgreSQL)
| Переменная     | Значение по умолчанию | Назначение                               |
|----------------|-----------------------|-------------------------------------------|
| `DB_HOST`      | `postgres`            | Хост PostgreSQL в сети Docker             |
| `DB_PORT`      | `5432`                | Порт PostgreSQL внутри сети               |
| `DB_NAME`      | `healthity_db`        | Имя базы данных                           |
| `DB_USER`      | `postgres`            | Пользователь БД                           |
| `DB_PASSWORD`  | `postgres`            | Пароль пользователя БД                    |
| `DB_ECHO`      | `false`               | Логирование SQL запросов (для отладки)    |

### Redis
| Переменная     | Значение по умолчанию | Назначение                               |
|----------------|-----------------------|-------------------------------------------|
| `REDIS_HOST`   | `redis`               | Хост Redis                                |
| `REDIS_PORT`   | `6379`                | Порт Redis                                |
| `REDIS_PASSWORD` | `None`              | Пароль Redis (опционально)                |

### RabbitMQ
| Переменная     | Значение по умолчанию | Назначение                               |
|----------------|-----------------------|-------------------------------------------|
| `RABBIT_HOST`  | `rabbitmq`            | Хост RabbitMQ (для сетевого доступа)      |
| `RABBIT_PORT`  | `5672`                | AMQP порт RabbitMQ                        |
| `RABBIT_WEB_PORT` | `15673`            | Порт RabbitMQ Management UI               |
| `RABBIT_USER`  | `healthity_rabbit_user` | Пользователь приложения                  |
| `RABBIT_PASSWORD` | `healthity_rabbit_password` | Пароль приложения                |
| `RABBITMQ_DEFAULT_USER` | `admin`     | Админ для initial seed                    |
| `RABBITMQ_DEFAULT_PASS` | `admin`     | Пароль адм. пользователя                  |

### JWT (Authentication)
| Переменная     | Значение по умолчанию | Назначение                               |
|----------------|-----------------------|-------------------------------------------|
| `JWT_SECRET_KEY` | *обязательно*       | Секретный ключ для подписи JWT токенов    |
| `JWT_ALGORITHM` | `HS256`              | Алгоритм шифрования JWT                   |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Время жизни access токена (минуты)   |
| `JWT_REFRESH_TOKEN_EXPIRE_MINUTES` | `10080` | Время жизни refresh токена (7 дней) |

**Пример `.env` файла:**
```env
# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=healthity_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_ECHO=false

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# RabbitMQ
RABBIT_HOST=rabbitmq
RABBIT_PORT=5672
RABBIT_WEB_PORT=15673
RABBIT_USER=healthity_rabbit_user
RABBIT_PASSWORD=healthity_rabbit_password
RABBITMQ_DEFAULT_USER=admin
RABBITMQ_DEFAULT_PASS=admin

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_MINUTES=10080
```

> ⚠️ **Важно:** Измените `JWT_SECRET_KEY` на случайную строку в production окружении!

### 2. Сборка и запуск контейнеров

```bash
make app-build   # сборка образов (по умолчанию использует .env)
make app         # запуск приложения + postgres + redis + rabbitmq
```

**После запуска доступно:**
- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- RabbitMQ UI: `http://localhost:15673` (admin/admin)

Логи можно смотреть через:
```bash
docker logs healthity-backend-app -f
```

### 3. Управление инфраструктурой

- Миграции применяются автоматически при старте (`alembic upgrade head`). Для ручного запуска:

  ```bash
  docker compose --env-file .env -f docker-compose/app.yaml -f docker-compose/db.yaml -f docker-compose/rabbitmq.yaml exec app alembic upgrade head
  ```

- Остановка сервисов: `make app-down`
- Перезапуск стека: `make app-restart`
- Запуск только БД и Redis: `make app-db`

## 🔧 Особенности разработки

### Установка зависимостей
```bash
poetry install
```

### Миграции базы данных
```bash
# Создать новую миграцию
poetry run alembic revision --autogenerate -m "описание изменений"

# Применить миграции
poetry run alembic upgrade head

# Откатить миграцию
poetry run alembic downgrade -1
```

### Основные особенности

- **Python 3.13**
- **Асинхронность**: Все операции с БД выполняются асинхронно
- **UUID Primary Keys**: Все сущности используют UUID как первичные ключи
- **Temporal Fields**: Автоматические `created_at` и `updated_at` для аудита
- **Value Objects**: `TelegramId`, `Coin`, `Experience` для type-safety
- **JWT Authentication**: Secure token-based auth с refresh tokens
- **Transaction Logging**: Все финансовые операции логируются
- **Ownership Checks**: Пользователи могут управлять только своими данными

### Архитектурные паттерны

1. **Repository Pattern**: Абстракция доступа к данным
2. **Unit of Work**: Транзакционность операций
3. **Dependency Injection**: Слабая связанность компонентов
4. **DTO Pattern**: Разделение API схем и доменных сущностей
5. **Use Case Pattern**: Инкапсуляция бизнес-логики

## 📝 Полезные команды

| Команда | Описание |
|---------|----------|
| `make app` | Запуск полного стека (приложение + Postgres + Redis + RabbitMQ) |
| `make app-build` | Сборка Docker образов |
| `make app-down` | Остановка всех сервисов |
| `make app-restart` | Перезапуск стека |
| `make app-db` | Запуск только PostgreSQL и Redis для диагностики |
| `docker logs healthity-backend-app -f` | Просмотр логов приложения |
| `poetry install` | Установка зависимостей локально |
| `poetry run alembic upgrade head` | Применение миграций |

## 🧪 Тестирование API

### Примеры запросов

**Получить JWT токен:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": 123456789, "password": "your_password"}'
```

**Получить информацию о пользователе:**
```bash
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Просмотреть каталог предметов (без авторизации):**
```bash
curl -X GET http://localhost:8000/api/v1/items/catalog
```

Полная документация запросов доступна в [API_DOCUMENTATION.md](src/drivers/rest/API_DOCUMENTATION.md)

## 🔐 Безопасность

- **JWT токены** для аутентификации пользователей
- **Bcrypt** для хеширования паролей
- **Ownership checks** на уровне use cases
- **Admin-only routes** для административных операций
- **Валидация данных** через Pydantic schemas
- **SQL Injection защита** через SQLAlchemy ORM
- **CORS настройки** для безопасных cross-origin запросов

## 🚀 Основные функции

### Для пользователей
- ✅ Регистрация и аутентификация через Telegram ID
- ✅ Создание и управление персонажем
- ✅ Покупка предметов и фонов за внутриигровую валюту
- ✅ Отслеживание дневных активностей
- ✅ Запись истории настроения
- ✅ Просмотр статистики и прогресса
- ✅ Управление друзьями
- ✅ Настройки уведомлений (режим "не беспокоить")

### Для администраторов
- ✅ Управление пользователями
- ✅ Управление каталогом (предметы, фоны, типы активностей)
- ✅ Ручное пополнение/списание баланса
- ✅ Просмотр всех транзакций

## 📊 База данных

### Основные таблицы
- `users` - Пользователи системы
- `characters` - Персонажи пользователей
- `items` - Каталог предметов
- `backgrounds` - Каталог фонов
- `character_items` - Купленные предметы персонажей
- `character_backgrounds` - Купленные фоны персонажей
- `transactions` - История финансовых операций
- `daily_activities` - Дневные активности
- `daily_progress` - Дневной прогресс персонажей
- `mood_history` - История настроения
- `user_friends` - Связи дружбы между пользователями
- `user_settings` - Настройки пользователей

## 📚 Дополнительные материалы

- [API Documentation](src/drivers/rest/API_DOCUMENTATION.md) - Полная документация API
- [Swagger UI](http://localhost:8000/docs) - Интерактивная документация
- [ReDoc](http://localhost:8000/redoc) - Альтернативная документация

## 📄 Лицензия

Проект распространяется под лицензией Apache 2.0. Информацию о лицензировании зависимостей смотрите в их репозиториях.
