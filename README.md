# Бэкенд Healthity

Сервис на FastAPI, отвечающий за хранение пользователей Telegram, управление персонажами, предметами, активностями и работу бизнес-логики через use-case-слой. В качестве хранилищ используются PostgreSQL и Redis, взаимодействие организовано через асинхронные репозитории и контейнер зависимостей.

## 📖 Документация API

Полная документация API доступна в файле [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

**Интерактивная документация:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

**Основные endpoints:**
- 🔐 Аутентификация: `/api/v1/auth/telegram/*` (Telegram Mini App)
- 👤 Пользователи: `/api/v1/users/*` (регистрация, `/me`, админские)
- 🎮 Персонажи: `/api/v1/characters/*` (`/me`, админские)
- 🛍️ Каталоги (открытые): `/api/v1/{items,backgrounds,activity-types,item-categories}/catalog`
- 💰 Покупки: `/api/v1/character-{items,backgrounds}/me/purchase`
- 📊 Активности: `/api/v1/daily-activities/*`, `/api/v1/base-character-activities/*`
- 📈 Прогресс: `/api/v1/daily-progress/*`
- 😊 Настроение: `/api/v1/mood-history/*`
- 👥 Друзья: `/api/v1/user-friends/*`
- ⚙️ Настройки: `/api/v1/user-settings/me`
- 💳 Транзакции: `/api/v1/transactions/*`
- 📍 Позиции: `/api/v1/item-background-positions/*` (только админские)

## 🛠️ Стек технологий

- **Python 3.13**, FastAPI, Starlette
- **SQLAlchemy 2** с асинхронным движком и миграциями Alembic
- **PostgreSQL** (через asyncpg), **Redis** и **RabbitMQ**
- **Dependency Injector** для управления зависимостями
- **Telegram Mini App Auth** для авторизации через Telegram
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
    auth/                # JWT сервис, провайдеры токенов, Telegram Mini App Auth
    settings.py          # Конфигурация на базе Pydantic
    security.py          # Хеширование паролей
  domain/                # Доменный слой
    entities/            # Доменные сущности (User, Character, Item, etc.)
    exceptions.py        # Доменные исключения
  drivers/rest/          # REST API транспортный слой
    schemas/             # Pydantic схемы для API
    *.py                 # Роуты FastAPI
  ports/                 # Порты (интерфейсы репозиториев)
    repositories/        # Абстрактные классы репозиториев
  use_cases/             # Бизнес-логика (Use Cases)
    users/               # Use cases для пользователей
    characters/          # Use cases для персонажей
    items/               # Use cases для предметов
    backgrounds/         # Use cases для фонов
    character_items/     # Use cases для предметов персонажа
    character_backgrounds/ # Use cases для фонов персонажа
    item_background_positions/ # Use cases для позиций предметов
    activity_types/      # Use cases для типов активностей
    base_character_activities/ # Use cases для базовых активностей
    daily_activities/    # Use cases для дневных активностей
    daily_progress/      # Use cases для дневного прогресса
    mood_history/        # Use cases для настроения
    transactions/        # Use cases для транзакций
    user_friends/        # Use cases для друзей
    user_settings/       # Use cases для настроек
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
| `DB_USER`      | `healthity`           | Пользователь БД                           |
| `DB_PASSWORD`  | *обязательно*         | Пароль пользователя БД                    |
| `DB_ECHO`      | `false`               | Логирование SQL запросов (для отладки)    |
| `DB_HOST_PORT` | `5433`                | Loopback-порт PostgreSQL для локального compose |

### Redis
| Переменная     | Значение по умолчанию | Назначение                               |
|----------------|-----------------------|-------------------------------------------|
| `REDIS_HOST`   | `redis`               | Хост Redis                                |
| `REDIS_PORT`   | `6379`                | Порт Redis                                |
| `REDIS_PASSWORD` | *обязательно*      | Пароль Redis                              |
| `REDIS_HOST_PORT` | `6378`            | Loopback-порт Redis для локального compose |

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

### Telegram Mini App
| Переменная     | Значение по умолчанию | Назначение                               |
|----------------|-----------------------|-------------------------------------------|
| `TELEGRAM_BOT_TOKEN` | *обязательно*    | Токен Telegram бота для валидации Init Data |

**Пример `.env` файла:**
```env
# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=healthity_db
DB_USER=healthity
DB_PASSWORD=change_me_strong_password
DB_ECHO=false
DB_HOST_PORT=5433

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=change_me_strong_password
REDIS_HOST_PORT=6378

# RabbitMQ
RABBIT_HOST=rabbitmq
RABBIT_PORT=5672
RABBIT_WEB_PORT=15673
RABBIT_USER=healthity_rabbit_user
RABBIT_PASSWORD=healthity_rabbit_password
RABBITMQ_DEFAULT_USER=admin
RABBITMQ_DEFAULT_PASS=admin

# Telegram
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

> ⚠️ **Важно:** Измените `TELEGRAM_BOT_TOKEN` на реальное значение в production окружении!

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
- **Telegram Mini App Auth**: Авторизация через Telegram Init Data
- **Transaction Logging**: Все финансовые операции логируются
- **Ownership Checks**: Пользователи могут управлять только своими данными
- **Cascade Deletion**: Каскадное удаление связанных сущностей (activity_types, items, backgrounds)

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

**Регистрация пользователя:**
```bash
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Authorization: Bearer {telegram_init_data}" \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": 123456789, "password": "optional_password"}'
```

**Получить информацию о пользователе (Telegram Mini App):**
```bash
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer {telegram_init_data}"
```

**Просмотреть каталог предметов (без авторизации):**
```bash
curl -X GET http://localhost:8000/api/v1/items/catalog
```

**Админский запрос (Basic Auth):**
```bash
curl -X GET http://localhost:8000/api/v1/users/admin \
  -H "Authorization: Basic {base64_encoded_credentials}"
```

Полная документация запросов доступна в [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## 🔐 Безопасность

- **Telegram Mini App Init Data** для авторизации через Telegram (для пользовательских эндпоинтов `/me`)
- **Basic Authentication** для админских эндпоинтов
- **Bcrypt** для хеширования паролей
- **Ownership checks** на уровне use cases
- **Admin-only routes** для административных операций
- **Валидация данных** через Pydantic schemas
- **SQL Injection защита** через SQLAlchemy ORM
- **CORS настройки** для безопасных cross-origin запросов

## 🚀 Основные функции

### Для пользователей
- ✅ Регистрация и аутентификация через Telegram ID (пароль опционален)
- ✅ Создание и управление персонажем
- ✅ Покупка предметов и фонов за внутриигровую валюту
- ✅ Управление предметами и фонами (активация, избранное)
- ✅ Отслеживание дневных активностей и прогресса
- ✅ Запись истории настроения
- ✅ Просмотр статистики и прогресса
- ✅ Управление друзьями (добавление, удаление, просмотр информации)
- ✅ Настройки уведомлений (режим "не беспокоить")
- ✅ Управление базовыми активностями персонажа

### Для администраторов
- ✅ Управление пользователями (CRUD)
- ✅ Управление каталогом (предметы, фоны, типы активностей, категории)
- ✅ Управление персонажами и их данными
- ✅ Управление предметами и фонами персонажей
- ✅ Управление позициями предметов на фонах
- ✅ Ручное пополнение/списание баланса
- ✅ Просмотр всех транзакций
- ✅ Управление активностями и прогрессом
- ✅ Управление историей настроения
- ✅ Управление друзьями пользователей

## 📊 База данных

### Основные таблицы
- `users` - Пользователи системы
- `characters` - Персонажи пользователей
- `items` - Каталог предметов
- `item_categories` - Категории предметов
- `backgrounds` - Каталог фонов
- `character_items` - Купленные предметы персонажей
- `character_backgrounds` - Купленные фоны персонажей
- `item_background_positions` - Позиции предметов на фонах
- `activity_types` - Типы активностей
- `base_character_activities` - Базовые активности персонажей
- `daily_activities` - Дневные активности
- `daily_progress` - Дневной прогресс персонажей
- `mood_history` - История настроения
- `transactions` - История финансовых операций
- `user_friends` - Связи дружбы между пользователями
- `user_settings` - Настройки пользователей

### Каскадное удаление
При удалении родительских сущностей автоматически удаляются связанные:
- При удалении `activity_type` удаляются связанные `base_character_activities` и `character_activity_history`
- При удалении `item` удаляются связанные `character_items` и `item_background_positions`
- При удалении `background` удаляются связанные `character_backgrounds` и `item_background_positions`

**Примечание:** Удаление `item_category` невозможно, если есть связанные `items` (RESTRICT).

## 📚 Дополнительные материалы

- [API Documentation](API_DOCUMENTATION.md) - Полная документация API
- [Swagger UI](http://localhost:8000/docs) - Интерактивная документация
- [ReDoc](http://localhost:8000/redoc) - Альтернативная документация

## 📄 Лицензия

Проект распространяется под лицензией Apache 2.0. Информацию о лицензировании зависимостей смотрите в их репозиториях.
