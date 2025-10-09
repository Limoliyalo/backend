# Бэкенд Healthity

Сервис на FastAPI, отвечающий за хранение пользователей Telegram, управление коллекционными изображениями и работу бизнес-логики через use-case-слой. В качестве хранилищ используются PostgreSQL и Redis, взаимодействие организовано через асинхронные репозитории и контейнер зависимостей.

## Стек технологий

- **Python 3.12**, FastAPI, Starlette;
- **SQLAlchemy 2** с асинхронным движком и миграциями Alembic;
- **PostgreSQL** (через asyncpg), **Redis** и **RabbitMQ**;
- **Dependency Injector** для сборки зависимостей;
- **Docker Compose** для локальной инфраструктуры.

## Структура проекта

```
src/
  adapters/
    database/            # модели SQLAlchemy, сессии, миграции
    repositories/        # асинхронные репозитории пользователей и картинок
  core/settings.py       # конфигурация на базе Pydantic
  drivers/rest/          # транспортный слой FastAPI
  use_cases/             # бизнес-кейсы приложения
app.py                   # точка входа FastAPI с lifespan-хуками
container.py             # контейнер Dependency Injector
```

## Запуск проекта

### 1. Настройка окружения

При необходимости создайте или обновите файл `.env`:

```bash
cp .env.example .env  # если примера нет, создайте .env вручную
```

Ключевые переменные окружения:

| Переменная     | Значение по умолчанию | Назначение                               |
|----------------|-----------------------|-------------------------------------------|
| `DB_HOST`      | `postgres`            | хост PostgreSQL в сети Docker             |
| `DB_PORT`      | `5432`                | порт PostgreSQL внутри сети               |
| `DB_NAME`      | `healthity_db`        | имя базы данных                           |
| `DB_USER`      | `postgres`            | пользователь БД                           |
| `DB_PASSWORD`  | `postgres`            | пароль пользователя БД                    |
| `REDIS_HOST`   | `redis`               | хост Redis                                |
| `REDIS_PORT`   | `6379`                | порт Redis                                |
| `RABBIT_HOST`  | `rabbitmq`            | хост RabbitMQ (для сетевого доступа)      |
| `RABBIT_PORT`  | `5672`                | AMQP порт RabbitMQ                        |
| `RABBIT_WEB_PORT` | `15673`            | порт RabbitMQ Management UI               |
| `RABBIT_USER`  | `healthity_rabbit_user` | пользователь приложения                  |
| `RABBIT_PASSWORD` | `healthity_rabbit_password` | пароль приложения                |
| `RABBITMQ_DEFAULT_USER` | `admin`     | админ для initial seed                    |
| `RABBITMQ_DEFAULT_PASS` | `admin`     | пароль адм. пользователя                  |

### 2. Сборка и запуск контейнеров

```bash
make app-build   # сборка образов (по умолчанию использует .env)
make app         # запуск приложения + postgres + redis + rabbitmq
```

API будет доступно по адресу `http://localhost:8000`. RabbitMQ UI — `http://localhost:${RABBIT_WEB_PORT}` (по умолчанию 15673). Логи можно смотреть через `docker compose --env-file .env -f docker-compose/app.yaml -f docker-compose/db.yaml -f docker-compose/rabbitmq.yaml logs -f <service>`.

### 3. Управление инфраструктурой

- Миграции применяются автоматически при старте (`alembic upgrade head`). Для ручного запуска:

  ```bash
  docker compose --env-file .env -f docker-compose/app.yaml -f docker-compose/db.yaml -f docker-compose/rabbitmq.yaml exec app alembic upgrade head
  ```

- Остановка сервисов: `make app-down`
- Перезапуск стека: `make app-restart`
- Запуск только БД и Redis: `make app-db`

## Особенности разработки

- Используйте Python 3.12 и Poetry для локальной установки зависимостей: `poetry install`.
- `SessionManager` создаёт асинхронный движок SQLAlchemy и корректно закрывает соединение по завершении lifespan FastAPI.
- Модели используют UUID как первичные ключи и включают временные метки; записи картинок связываются с пользователями по Telegram ID.
- Новые миграции создаются командой `poetry run alembic revision --autogenerate -m "message"`, применяются `poetry run alembic upgrade head`.

## Полезные команды

| Команда | Описание |
|---------|----------|
| `make app` | запуск полного стека (приложение + Postgres + Redis + RabbitMQ); |
| `make app-down` | остановка всех сервисов; |
| `make app-restart` | перезапуск стека; |
| `make app-db` | запуск только PostgreSQL и Redis для диагностики. |

## Лицензия

Проект распространяется под лицензией Apache 2.0. Информацию о лицензировании зависимостей смотрите в их репозиториях.
