# API Documentation - Healthity Backend

## Оглавление
- [Общая информация](#общая-информация)
- [Аутентификация](#аутентификация)
- [Пользователи (Users)](#пользователи-users)
- [Персонажи (Characters)](#персонажи-characters)
- [Предметы (Items)](#предметы-items)
- [Фоны (Backgrounds)](#фоны-backgrounds)
- [Типы активностей (Activity Types)](#типы-активностей-activity-types)
- [Дневные активности (Daily Activities)](#дневные-активности-daily-activities)
- [Дневной прогресс (Daily Progress)](#дневной-прогресс-daily-progress)
- [История настроения (Mood History)](#история-настроения-mood-history)
- [Транзакции (Transactions)](#транзакции-transactions)
- [Друзья (Friends)](#друзья-friends)
- [Настройки пользователя (User Settings)](#настройки-пользователя-user-settings)
- [Коды ошибок](#коды-ошибок)

---

## Общая информация

**Base URL:** `http://localhost:8000/api/v1`

**Формат данных:** JSON

**Авторизация:** JWT Bearer Token (для большинства endpoints)

**Timezone:** Все даты в UTC (ISO 8601 format)

---

## Аутентификация

### Получить JWT токен
```http
POST /auth/token
Content-Type: application/json

{
  "telegram_id": 123456789,
  "password": "user_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Обновить токен
```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Protected Endpoint (пример использования токена)
```http
GET /auth/protected
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Пользователи (Users)

### 👤 Получить информацию о текущем пользователе
```http
GET /users/me
Authorization: Bearer {token}
```

**Response:**
```json
{
  "telegram_id": 123456789,
  "is_active": true,
  "balance": 1000,
  "password_hash": "...",
  "created_at": "2025-10-12T12:00:00Z",
  "updated_at": "2025-10-12T12:00:00Z"
}
```

### 💰 Пополнить баланс
```http
POST /users/me/deposit
Authorization: Bearer {token}
Content-Type: application/json

{
  "amount": 100
}
```

### 💸 Списать средства с баланса
```http
POST /users/me/withdraw
Authorization: Bearer {token}
Content-Type: application/json

{
  "amount": 50
}
```

### 📊 Получить статистику пользователя
```http
GET /users/me/statistics
Authorization: Bearer {token}
```

**Response:**
```json
{
  "user_id": 123456789,
  "balance": 1000,
  "level": 5,
  "total_experience": 500,
  "character_name": "John",
  "character_sex": "male",
  "purchased_items_count": 10,
  "purchased_backgrounds_count": 5,
  "mood_entries_count": 50,
  "activities_count": 30,
  "total_transactions": 15,
  "friends_count": 8
}
```

### 🔐 Изменить пароль
```http
POST /users/me/change-password
Authorization: Bearer {token}
Content-Type: application/json

{
  "old_password": "old_pass",
  "new_password": "new_pass"
}
```

---

## Персонажи (Characters)

### 👥 Получить своего персонажа
```http
GET /characters/me
Authorization: Bearer {token}
```

### ➕ Создать персонажа (только безопасные поля)
```http
POST /characters/me
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "John",
  "sex": "male"
}
```
**Примечание:** `current_mood`, `level`, `total_experience` устанавливаются сервером автоматически.

### ✏️ Обновить персонажа (только name и sex)
```http
PATCH /characters/me
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "New Name",
  "sex": "female"
}
```

### 🗑️ Удалить персонажа
```http
DELETE /characters/me
Authorization: Bearer {token}
```

---

## Предметы (Items)

### 🛍️ Просмотреть каталог предметов (открытый endpoint)
```http
GET /items/catalog
```

**Response:**
```json
[
  {
    "id": "uuid",
    "category_id": "uuid",
    "name": "Cool Hat",
    "description": "A very cool hat",
    "cost": 100,
    "required_level": 1,
    "is_available": true,
    "created_at": "2025-10-12T12:00:00Z",
    "updated_at": "2025-10-12T12:00:00Z"
  }
]
```

### 🎒 Просмотреть свои купленные предметы
```http
GET /character-items/me
Authorization: Bearer {token}
```

### 🛒 Купить предмет
```http
POST /character-items/purchase?item_id={uuid}
Authorization: Bearer {token}
```

### 👕 Надеть предмет
```http
PATCH /character-items/{character_item_id}/equip
Authorization: Bearer {token}
```

### 👔 Снять предмет
```http
PATCH /character-items/{character_item_id}/unequip
Authorization: Bearer {token}
```

### ⭐ Добавить/убрать предмет из избранного
```http
PATCH /character-items/{character_item_id}/favourite
Authorization: Bearer {token}
```

---

## Фоны (Backgrounds)

### 🖼️ Просмотреть каталог фонов (открытый endpoint)
```http
GET /backgrounds/catalog
```

### 🎨 Просмотреть свои купленные фоны
```http
GET /character-backgrounds/me
Authorization: Bearer {token}
```

### 🛒 Купить фон
```http
POST /character-backgrounds/purchase?background_id={uuid}
Authorization: Bearer {token}
```

### ✅ Активировать фон
```http
PATCH /character-backgrounds/{character_background_id}/activate
Authorization: Bearer {token}
```

### ❌ Деактивировать фон
```http
PATCH /character-backgrounds/{character_background_id}/deactivate
Authorization: Bearer {token}
```

### ⭐ Добавить/убрать фон из избранного
```http
PATCH /character-backgrounds/{character_background_id}/favourite
Authorization: Bearer {token}
```

---

## Типы активностей (Activity Types)

### 📋 Просмотреть каталог типов активностей (открытый endpoint)
```http
GET /activity-types/catalog
```

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Walking",
    "unit": "steps",
    "color": "#FF5733",
    "daily_goal_default": 10000,
    "created_at": "2025-10-12T12:00:00Z"
  }
]
```

---

## Дневные активности (Daily Activities)

### 📅 Получить свои активности
```http
GET /daily-activities/me?day=2025-10-12T00:00:00Z
Authorization: Bearer {token}
```

**Или с диапазоном дат:**
```http
GET /daily-activities/me?start_date=2025-10-10T00:00:00Z&end_date=2025-10-12T23:59:59Z
Authorization: Bearer {token}
```

### ➕ Создать активность
```http
POST /daily-activities/me?activity_type_id={uuid}&date=2025-10-12T00:00:00Z&value=5000&goal=10000
Authorization: Bearer {token}
```

### ✏️ Обновить активность
```http
PATCH /daily-activities/{activity_id}/me
Authorization: Bearer {token}
Content-Type: application/json

{
  "value": 7500,
  "goal": 10000,
  "notes": "Good progress!"
}
```

---

## Дневной прогресс (Daily Progress)

### 📈 Получить свой дневной прогресс
```http
GET /daily-progress/me?limit=30
Authorization: Bearer {token}
```

**Или с диапазоном дат:**
```http
GET /daily-progress/me?start_date=2025-10-01T00:00:00Z&end_date=2025-10-12T23:59:59Z
Authorization: Bearer {token}
```

### 📊 Получить прогресс за конкретный день
```http
GET /daily-progress/me/day?day=2025-10-12T00:00:00Z
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "uuid",
  "character_id": "uuid",
  "date": "2025-10-12T00:00:00Z",
  "experience_gained": 50,
  "level_at_end": 5,
  "mood_average": "happy",
  "behavior_index": 85,
  "created_at": "2025-10-12T12:00:00Z",
  "updated_at": "2025-10-12T12:00:00Z"
}
```

---

## История настроения (Mood History)

### 😊 Получить историю настроения
```http
GET /mood-history/me?limit=100
Authorization: Bearer {token}
```

**Или с диапазоном дат:**
```http
GET /mood-history/me?start_date=2025-10-01T00:00:00Z&end_date=2025-10-12T23:59:59Z
Authorization: Bearer {token}
```

### ➕ Добавить запись о настроении
```http
POST /mood-history/me?mood=happy&trigger=exercise
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "uuid",
  "character_id": "uuid",
  "mood": "happy",
  "trigger": "exercise",
  "timestamp": "2025-10-12T12:00:00Z"
}
```

---

## Транзакции (Transactions)

### 💳 Получить свои транзакции
```http
GET /transactions/me
Authorization: Bearer {token}
```

**С фильтрацией по датам:**
```http
GET /transactions/me?start_date=2025-10-01T00:00:00Z&end_date=2025-10-12T23:59:59Z
Authorization: Bearer {token}
```

**С фильтрацией по типу:**
```http
GET /transactions/me?transaction_type=deposit
Authorization: Bearer {token}
```

**Типы транзакций:**
- `deposit` - пополнение
- `withdrawal` - списание
- `purchase_item` - покупка предмета
- `purchase_background` - покупка фона

**Response:**
```json
[
  {
    "id": "uuid",
    "user_tg_id": 123456789,
    "amount": 100,
    "balance_after": 1100,
    "type": "deposit",
    "related_item_id": null,
    "related_background_id": null,
    "description": "Пополнение баланса",
    "timestamp": "2025-10-12T12:00:00Z"
  }
]
```

---

## Друзья (Friends)

### 👥 Получить список своих друзей
```http
GET /user-friends/me
Authorization: Bearer {token}
```

### ➕ Добавить друга
```http
POST /user-friends/me
Authorization: Bearer {token}
Content-Type: application/json

{
  "friend_tg_id": 987654321
}
```

### 🗑️ Удалить друга
```http
DELETE /user-friends/me/{friend_tg_id}
Authorization: Bearer {token}
```

---

## Настройки пользователя (User Settings)

### ⚙️ Получить свои настройки
```http
GET /user-settings/me
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "uuid",
  "user_tg_id": 123456789,
  "quiet_start_time": "22:00:00",
  "quiet_end_time": "08:00:00",
  "muted_days": ["saturday", "sunday"],
  "do_not_disturb": false,
  "created_at": "2025-10-12T12:00:00Z",
  "updated_at": "2025-10-12T12:00:00Z"
}
```

### ✏️ Обновить настройки
```http
PUT /user-settings/me
Authorization: Bearer {token}
Content-Type: application/json

{
  "quiet_start_time": "23:00:00",
  "quiet_end_time": "07:00:00",
  "muted_days": ["sunday"],
  "do_not_disturb": true
}
```

### 🗑️ Удалить настройки
```http
DELETE /user-settings/me
Authorization: Bearer {token}
```

---

## Категории предметов (Item Categories)

### 📂 Просмотреть каталог категорий (открытый endpoint)
```http
GET /item-categories/catalog
```

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Hats",
    "description": "Various hats and headwear",
    "created_at": "2025-10-12T12:00:00Z"
  }
]
```

---

## Коды ошибок

### HTTP Status Codes

| Код | Описание |
|-----|----------|
| 200 | OK - Успешный запрос |
| 201 | Created - Ресурс создан |
| 204 | No Content - Успешно, нет контента |
| 400 | Bad Request - Неверный запрос |
| 401 | Unauthorized - Требуется авторизация |
| 403 | Forbidden - Доступ запрещен |
| 404 | Not Found - Ресурс не найден |
| 422 | Unprocessable Entity - Ошибка валидации |
| 500 | Internal Server Error - Ошибка сервера |

### Формат ответа с ошибкой

```json
{
  "detail": "User with telegram_id 123456789 not found"
}
```

### Примеры ошибок

**Недостаточно средств:**
```json
{
  "detail": "Insufficient balance"
}
```

**Предмет уже куплен:**
```json
{
  "detail": "Item already purchased"
}
```

**Ресурс не найден:**
```json
{
  "detail": "Character for user 123456789 not found"
}
```

**Ошибка авторизации:**
```json
{
  "detail": "Could not validate credentials"
}
```

---

## Примечания

### 🔒 Безопасность
- Все пользовательские endpoints требуют JWT авторизацию
- `telegram_id` извлекается из JWT токена, не передается в body/query
- Пользователи могут управлять только своими данными
- Проверка владения ресурсами выполняется на стороне сервера

### 📝 Ограничения
- Пользователи могут создавать персонажей, указывая только `name` и `sex`
- Серверные поля (`level`, `experience`, `mood`) управляются автоматически
- Покупка проверяет баланс и доступность товара
- Все транзакции логируются

### 🌐 Открытые endpoints (без авторизации)
- `GET /items/catalog`
- `GET /backgrounds/catalog`
- `GET /activity-types/catalog`
- `GET /item-categories/catalog`

Эти endpoints доступны для всех и используются для отображения каталога в магазине.

---

## Swagger UI

Интерактивная документация доступна по адресу:
```
http://localhost:8000/docs
```

ReDoc документация:
```
http://localhost:8000/redoc
```

