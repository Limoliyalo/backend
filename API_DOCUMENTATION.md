# API Documentation - Healthity Backend

## Оглавление
- [Общая информация](#общая-информация)
- [Аутентификация](#аутентификация)
- [Пользователи (Users)](#пользователи-users)
- [Персонажи (Characters)](#персонажи-characters)
- [Предметы (Items)](#предметы-items)
- [Категории предметов (Item Categories)](#категории-предметов-item-categories)
- [Фоны (Backgrounds)](#фоны-backgrounds)
- [Предметы персонажа (Character Items)](#предметы-персонажа-character-items)
- [Фоны персонажа (Character Backgrounds)](#фоны-персонажа-character-backgrounds)
- [Позиции предметов на фонах (Item Background Positions)](#позиции-предметов-на-фонах-item-background-positions)
- [Типы активностей (Activity Types)](#типы-активностей-activity-types)
- [Базовые активности персонажа (Base Character Activities)](#базовые-активности-персонажа-base-character-activities)
- [Дневные активности (Daily Activities)](#дневные-активности-daily-activities)
- [Дневной прогресс (Daily Progress)](#дневной-прогресс-daily-progress)
- [История настроения (Mood History)](#история-настроения-mood-history)
- [Транзакции (Transactions)](#транзакции-transactions)
- [Друзья (User Friends)](#друзья-user-friends)
- [Настройки пользователя (User Settings)](#настройки-пользователя-user-settings)
- [Коды ошибок](#коды-ошибок)

---

## Общая информация

**Base URL:** `http://localhost:8000/api/v1`

**Формат данных:** JSON

**Авторизация:**
- **Admin endpoints**: Basic Authentication (username:password в base64)
- **User endpoints (/me)**: Bearer Token (Telegram Mini App Init Data)

**Timezone:** Все даты в UTC (ISO 8601 format)

---

## Аутентификация

### Регистрация пользователя
```http
POST /users/register
Content-Type: application/json

{
  "telegram_id": 123456789,
  "password": "user_password"  // опционально - можно не указывать, минимум 6 символов
}
```

Registration is a legacy public compatibility endpoint. Other user-specific
endpoints still require `Authorization: Bearer {telegram_init_data}`.

**Response:**
```json
{
  "telegram_id": 123456789,
  "is_active": true,
  "balance": 0,
  "password_hash": "...",
  "created_at": "2025-10-12T12:00:00Z",
  "updated_at": "2025-10-12T12:00:00Z"
}
```

### Telegram Mini App Авторизация

Все пользовательские эндпоинты (`/me`) используют авторизацию через Telegram Mini App Init Data. Это означает, что вместо JWT токенов используется специальный формат данных от Telegram.

#### Получить данные Telegram пользователя
```http
GET /auth/telegram/me
Authorization: Bearer {telegram_init_data}
```

**Response:**
```json
{
  "user": {
    "id": 123456789,
    "first_name": "John",
    "last_name": "Doe",
    "username": "johndoe",
    "language_code": "en",
    "is_premium": false,
    "photo_url": "https://..."
  },
  "auth_date": 1697123456
}
```

#### Получить Telegram User ID
```http
GET /auth/telegram/user-id
Authorization: Bearer {telegram_init_data}
```

**Response:**
```json
{
  "user_id": 123456789
}
```

#### Проверка авторизации (protected endpoint)
```http
GET /auth/telegram/protected
Authorization: Bearer {telegram_init_data}
```

**Response:**
```json
{
  "message": "Telegram Mini App authentication successful",
  "user_id": 123456789
}
```

**Примечание:** `telegram_init_data` - это строка в формате query string, содержащая данные от Telegram Mini App. Формат: `query_id=...&user={...}&auth_date=...&hash=...`

**Пример использования:**
```http
GET /users/me
Authorization: Bearer {telegram_init_data}
```

---

## Пользователи (Users)

### 👤 Получить информацию о текущем пользователе
```http
GET /users/me
Authorization: Bearer {telegram_init_data}
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
Authorization: Bearer {telegram_init_data}
Content-Type: application/json

{
  "amount": 100
}
```

### 💸 Списать средства с баланса
```http
POST /users/me/withdraw
Authorization: Bearer {telegram_init_data}
Content-Type: application/json

{
  "amount": 50
}
```

### 📊 Получить статистику пользователя
```http
GET /users/me/statistics
Authorization: Bearer {telegram_init_data}
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
Authorization: Bearer {telegram_init_data}
Content-Type: application/json

{
  "old_password": "old_pass",
  "new_password": "new_pass"
}
```

### 🔧 Админские эндпоинты

#### Список пользователей
```http
GET /users/admin?limit=100&offset=0
Authorization: Basic {base64_encoded_credentials}
```

#### Получить пользователя по Telegram ID
```http
GET /users/{telegram_id}/admin
Authorization: Basic {base64_encoded_credentials}
```

#### Создать пользователя
```http
POST /users/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "telegram_id": 123456789,
  "password": "password",
  "is_active": true,
  "balance": 0
}
```

#### Обновить пользователя
```http
PUT /users/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "telegram_id": 123456789,
  "is_active": true,
  "balance": 100
}
```

#### Удалить пользователя
```http
DELETE /users/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "telegram_id": 123456789
}
```

---

## Персонажи (Characters)

### 👥 Получить своего персонажа
```http
GET /characters/me
Authorization: Bearer {telegram_init_data}
```

**Response:**
```json
{
  "id": "uuid",
  "user_tg_id": 123456789,
  "name": "John",
  "sex": "male",
  "current_mood": "happy",
  "level": 5,
  "total_experience": 100,
  "created_at": "2025-10-12T12:00:00Z",
  "updated_at": "2025-10-12T12:00:00Z"
}
```

### ➕ Создать персонажа
```http
POST /characters/me
Authorization: Bearer {telegram_init_data}
Content-Type: application/json

{
  "name": "John",
  "sex": "male"
}
```

**Примечание:** `current_mood`, `level`, `total_experience` устанавливаются сервером автоматически.

### ✏️ Обновить персонажа
```http
PATCH /characters/me
Authorization: Bearer {telegram_init_data}
Content-Type: application/json

{
  "name": "New Name",
  "sex": "female"
}
```

### 🔧 Админские эндпоинты

#### Список персонажей
```http
GET /characters/admin?limit=100&offset=0
Authorization: Basic {base64_encoded_credentials}
```

#### Получить персонажа по ID
```http
GET /characters/{character_id}/admin
Authorization: Basic {base64_encoded_credentials}
```

#### Создать персонажа
```http
POST /characters/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "user_tg_id": 123456789,
  "name": "John",
  "sex": "male",
  "current_mood": "happy",
  "level": 1,
  "total_experience": 0
}
```

#### Обновить персонажа
```http
PATCH /characters/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "character_id": "uuid",
  "name": "New Name",
  "sex": "female",
  "current_mood": "sad",
  "level": 5,
  "total_experience": 100
}
```

#### Удалить персонажа
```http
DELETE /characters/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "character_id": "uuid"
}
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

### ⭐ Переключить избранное для предмета
```http
POST /items/me/toggle-favorite
Authorization: Bearer {telegram_init_data}
Content-Type: application/json

{
  "item_id": "uuid"
}
```

### 🔧 Админские эндпоинты

#### Список предметов
```http
GET /items/admin?limit=100&offset=0
Authorization: Basic {base64_encoded_credentials}
```

#### Получить предмет по ID
```http
GET /items/{item_id}/admin
Authorization: Basic {base64_encoded_credentials}
```

#### Создать предмет
```http
POST /items/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "category_id": "uuid",
  "name": "Cool Hat",
  "description": "A very cool hat",
  "cost": 100,
  "required_level": 1,
  "is_available": true
}
```

#### Обновить предмет
```http
PATCH /items/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "item_id": "uuid",
  "name": "Updated Name",
  "cost": 150,
  "is_available": false
}
```

#### Удалить предмет
```http
DELETE /items/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "item_id": "uuid"
}
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

### 🔧 Админские эндпоинты

#### Список категорий
```http
GET /item-categories/admin?limit=100&offset=0
Authorization: Basic {base64_encoded_credentials}
```

#### Получить категорию по ID
```http
GET /item-categories/{category_id}/admin
Authorization: Basic {base64_encoded_credentials}
```

#### Создать категорию
```http
POST /item-categories/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "name": "Hats",
  "description": "Various hats and headwear"
}
```

#### Обновить категорию
```http
PATCH /item-categories/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "category_id": "uuid",
  "name": "Updated Name",
  "description": "Updated description"
}
```

#### Удалить категорию
```http
DELETE /item-categories/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "category_id": "uuid"
}
```

**Примечание:** Удаление категории невозможно, если есть связанные предметы.

---

## Фоны (Backgrounds)

### 🖼️ Просмотреть каталог фонов (открытый endpoint)
```http
GET /backgrounds/catalog
```

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Forest",
    "description": "Beautiful forest background",
    "cost": 200,
    "required_level": 2,
    "is_available": true,
    "created_at": "2025-10-12T12:00:00Z",
    "updated_at": "2025-10-12T12:00:00Z"
  }
]
```

### ⭐ Переключить избранное для фона
```http
POST /backgrounds/me/toggle-favorite
Authorization: Bearer {telegram_init_data}
Content-Type: application/json

{
  "background_id": "uuid"
}
```

### 🔧 Админские эндпоинты

#### Список фонов
```http
GET /backgrounds/admin?limit=100&offset=0
Authorization: Basic {base64_encoded_credentials}
```

#### Получить фон по ID
```http
GET /backgrounds/{background_id}/admin
Authorization: Basic {base64_encoded_credentials}
```

#### Создать фон
```http
POST /backgrounds/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "name": "Forest",
  "description": "Beautiful forest background",
  "cost": 200,
  "required_level": 2,
  "is_available": true
}
```

#### Обновить фон
```http
PATCH /backgrounds/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "background_id": "uuid",
  "name": "Updated Name",
  "cost": 250,
  "is_available": false
}
```

#### Удалить фон
```http
DELETE /backgrounds/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "background_id": "uuid"
}
```

---

## Предметы персонажа (Character Items)

### 🎒 Просмотреть свои купленные предметы
```http
GET /character-items/me
Authorization: Bearer {telegram_init_data}
```

**Response:**
```json
[
  {
    "id": "uuid",
    "character_id": "uuid",
    "item_id": "uuid",
    "is_active": false,
    "is_favorite": true,
    "is_purchased": true
  }
]
```

### 🛒 Купить предмет
```http
POST /character-items/me/purchase
Authorization: Bearer {telegram_init_data}
Content-Type: application/json

{
  "item_id": "uuid"
}
```

**Примечание:** С баланса пользователя списывается стоимость предмета.

### 👕 Активировать предмет
```http
PATCH /character-items/me/equip
Authorization: Bearer {telegram_init_data}
Content-Type: application/json

{
  "character_item_id": "uuid"
}
```

### 👔 Деактивировать предмет
```http
PATCH /character-items/me/unequip
Authorization: Bearer {telegram_init_data}
Content-Type: application/json

{
  "character_item_id": "uuid"
}
```

### 🔧 Админские эндпоинты

#### Список предметов персонажа
```http
GET /character-items/admin?character_id={uuid}
Authorization: Basic {base64_encoded_credentials}
```

#### Получить предмет персонажа по ID
```http
GET /character-items/{character_item_id}/admin
Authorization: Basic {base64_encoded_credentials}
```

#### Создать предмет для персонажа
```http
POST /character-items/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "character_id": "uuid",
  "item_id": "uuid",
  "is_active": false,
  "is_favorite": false
}
```

#### Обновить предмет персонажа
```http
PATCH /character-items/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "character_item_id": "uuid",
  "is_active": true,
  "is_favorite": true
}
```

#### Удалить предмет персонажа
```http
DELETE /character-items/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "character_item_id": "uuid"
}
```

---

## Фоны персонажа (Character Backgrounds)

### 🎨 Просмотреть свои купленные фоны
```http
GET /character-backgrounds/me
Authorization: Bearer {telegram_init_data}
```

**Response:**
```json
[
  {
    "id": "uuid",
    "character_id": "uuid",
    "background_id": "uuid",
    "is_active": false,
    "is_favorite": true,
    "is_purchased": true
  }
]
```

### Получить фон по ID
```http
GET /character-backgrounds/me/{background_id}
Authorization: Bearer {telegram_init_data}
```

### 🛒 Купить фон
```http
POST /character-backgrounds/me/purchase
Authorization: Bearer {telegram_init_data}
Content-Type: application/json

{
  "background_id": "uuid"
}
```

**Примечание:** С баланса пользователя списывается стоимость фона.

### ✅ Активировать фон
```http
POST /character-backgrounds/me/equip
Authorization: Bearer {telegram_init_data}
Content-Type: application/json

{
  "background_id": "uuid"
}
```

### ❌ Деактивировать фон
```http
POST /character-backgrounds/me/unequip
Authorization: Bearer {telegram_init_data}
Content-Type: application/json

{
  "background_id": "uuid"
}
```

### ✏️ Обновить фон
```http
PUT /character-backgrounds/me
Authorization: Bearer {telegram_init_data}
Content-Type: application/json

{
  "background_id": "uuid",
  "is_active": false,
  "is_favorite": true
}
```

### 🔧 Админские эндпоинты

#### Список фонов персонажа
```http
GET /character-backgrounds/admin?character_id={uuid}
Authorization: Basic {base64_encoded_credentials}
```

#### Получить фон персонажа по ID
```http
GET /character-backgrounds/admin/{background_id}
Authorization: Basic {base64_encoded_credentials}
```

#### Создать фон для персонажа
```http
POST /character-backgrounds/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "character_id": "uuid",
  "background_id": "uuid",
  "is_active": false,
  "is_favorite": false
}
```

#### Обновить фон персонажа
```http
PUT /character-backgrounds/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "background_id": "uuid",
  "is_active": true,
  "is_favorite": true
}
```

#### Удалить фон персонажа
```http
DELETE /character-backgrounds/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "background_id": "uuid"
}
```

#### Экипировать фон
```http
POST /character-backgrounds/admin/equip
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "background_id": "uuid"
}
```

#### Снять фон
```http
POST /character-backgrounds/admin/unequip
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "background_id": "uuid"
}
```

#### Переключить избранное
```http
POST /character-backgrounds/admin/toggle-favorite
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "character_id": "uuid",
  "background_id": "uuid"
}
```

---

## Позиции предметов на фонах (Item Background Positions)

### 🔧 Админские эндпоинты

#### Список позиций для предмета на фоне
```http
GET /item-background-positions/admin?item_id={uuid}&background_id={uuid}
Authorization: Basic {base64_encoded_credentials}
```

**Response:**
```json
[
  {
    "id": "uuid",
    "item_id": "uuid",
    "background_id": "uuid",
    "position_x": 10.5,
    "position_y": 20.3,
    "position_z": 0.0
  }
]
```

#### Получить позицию по ID
```http
GET /item-background-positions/{position_id}/admin
Authorization: Basic {base64_encoded_credentials}
```

#### Создать позицию
```http
POST /item-background-positions/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "item_id": "uuid",
  "background_id": "uuid",
  "position_x": 10.5,
  "position_y": 20.3,
  "position_z": 0.0
}
```

#### Обновить позицию
```http
PUT /item-background-positions/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "position_id": "uuid",
  "position_x": 15.7,
  "position_y": 25.9,
  "position_z": 1.0
}
```

#### Удалить позицию
```http
DELETE /item-background-positions/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "position_id": "uuid"
}
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

### 🔧 Админские эндпоинты

#### Список типов активностей
```http
GET /activity-types/admin?limit=100&offset=0
Authorization: Basic {base64_encoded_credentials}
```

#### Получить тип активности по ID
```http
GET /activity-types/{activity_type_id}/admin
Authorization: Basic {base64_encoded_credentials}
```

#### Создать тип активности
```http
POST /activity-types/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "name": "Walking",
  "unit": "steps",
  "color": "#FF5733",
  "daily_goal_default": 10000
}
```

#### Обновить тип активности
```http
PATCH /activity-types/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "activity_type_id": "uuid",
  "name": "Running",
  "unit": "km",
  "color": "#00FF00",
  "daily_goal_default": 5000
}
```

#### Удалить тип активности
```http
DELETE /activity-types/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "activity_type_id": "uuid"
}
```

---

## Базовые активности персонажа (Base Character Activities)

### 📊 Получить свои базовые активности
```http
GET /base-character-activities/me
Authorization: Bearer {telegram_init_data}
```

**Response:**
```json
[
  {
    "id": "uuid",
    "character_id": "uuid",
    "activity_type_id": "uuid",
    "goal": 10000,
    "created_at": "2025-10-12T12:00:00Z",
    "updated_at": "2025-10-12T12:00:00Z"
  }
]
```

### ➕ Создать базовую активность
```http
POST /base-character-activities/me
Authorization: Bearer {telegram_init_data}
Content-Type: application/json

{
  "activity_type_id": "uuid",
  "goal": 10000
}
```

### ✏️ Обновить базовую активность
```http
PATCH /base-character-activities/me
Authorization: Bearer {telegram_init_data}
Content-Type: application/json

{
  "activity_id": "uuid",
  "goal": 15000
}
```

### 🔧 Админские эндпоинты

#### Список базовых активностей персонажа
```http
GET /base-character-activities/character/{character_id}/admin
Authorization: Basic {base64_encoded_credentials}
```

#### Получить базовую активность по ID
```http
GET /base-character-activities/{activity_id}/admin
Authorization: Basic {base64_encoded_credentials}
```

#### Создать базовую активность
```http
POST /base-character-activities/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "character_id": "uuid",
  "activity_type_id": "uuid",
  "goal": 10000
}
```

#### Обновить базовую активность
```http
PATCH /base-character-activities/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "activity_id": "uuid",
  "goal": 15000
}
```

#### Удалить базовую активность
```http
DELETE /base-character-activities/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "activity_id": "uuid"
}
```

---

## Дневные активности (Daily Activities)

### 📅 Получить свои активности за день
```http
GET /daily-activities/me?day=2025-10-12T00:00:00
Authorization: Bearer {telegram_init_data}
```

### 📅 Получить свои активности за диапазон дат
```http
GET /daily-activities/me?start_date=2025-10-01T00:00:00&end_date=2025-10-31T23:59:59
Authorization: Bearer {telegram_init_data}
```

**Response:**
```json
[
  {
    "id": "uuid",
    "character_id": "uuid",
    "activity_type_id": "uuid",
    "date": "2025-10-12T00:00:00Z",
    "value": 5000,
    "goal": 10000,
    "notes": "Good progress!",
    "created_at": "2025-10-12T12:00:00Z",
    "updated_at": "2025-10-12T12:00:00Z"
  }
]
```

### ➕ Создать активность
```http
POST /daily-activities/me
Authorization: Bearer {telegram_init_data}
Content-Type: application/json

{
  "activity_type_id": "uuid",
  "date": "2025-10-12T00:00:00Z",
  "value": 5000,
  "goal": 10000,
  "notes": "Good progress!"
}
```

### ✏️ Обновить активность
```http
PATCH /daily-activities/me
Authorization: Bearer {telegram_init_data}
Content-Type: application/json

{
  "activity_id": "uuid",
  "value": 7500,
  "goal": 10000,
  "notes": "Updated notes"
}
```

### 🔧 Админские эндпоинты

#### Список активностей персонажа за день
```http
GET /daily-activities/character/{character_id}/admin?day=2025-10-12T00:00:00
Authorization: Basic {base64_encoded_credentials}
```

#### Получить активность по ID
```http
GET /daily-activities/{activity_id}/admin
Authorization: Basic {base64_encoded_credentials}
```

#### Создать активность
```http
POST /daily-activities/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "character_id": "uuid",
  "activity_type_id": "uuid",
  "date": "2025-10-12T00:00:00Z",
  "value": 5000,
  "goal": 10000,
  "notes": "Good progress!"
}
```

#### Обновить активность
```http
PATCH /daily-activities/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "activity_id": "uuid",
  "value": 7500,
  "goal": 10000,
  "notes": "Updated notes"
}
```

#### Удалить активность
```http
DELETE /daily-activities/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "activity_id": "uuid"
}
```

---

## Дневной прогресс (Daily Progress)

### 📈 Получить свой прогресс за день
```http
GET /daily-progress/me?day=2025-10-12T00:00:00
Authorization: Bearer {telegram_init_data}
```

### 📈 Получить свой прогресс за диапазон дат
```http
GET /daily-progress/me?start_date=2025-10-01T00:00:00&end_date=2025-10-31T23:59:59
Authorization: Bearer {telegram_init_data}
```

**Response:**
```json
[
  {
    "id": "uuid",
    "character_id": "uuid",
    "date": "2025-10-12T00:00:00Z",
    "experience_gained": 50,
    "mood_average": "happy",
    "behavior_index": 85,
    "created_at": "2025-10-12T12:00:00Z",
    "updated_at": "2025-10-12T12:00:00Z"
  }
]
```

### ➕ Создать прогресс
```http
POST /daily-progress/me
Authorization: Bearer {telegram_init_data}
Content-Type: application/json

{
  "date": "2025-10-12T00:00:00Z",
  "experience_gained": 50,
  "mood_average": "happy",
  "behavior_index": 85
}
```

**Примечание:** `mood_average` может быть: `neutral`, `happy`, `sad`, `angry`, `bored`.

### 🔧 Админские эндпоинты

#### Список прогресса персонажа
```http
GET /daily-progress/character/{character_id}/admin
Authorization: Basic {base64_encoded_credentials}
```

#### Получить прогресс за день
```http
GET /daily-progress/character/{character_id}/day/admin?day=2025-10-12T00:00:00
Authorization: Basic {base64_encoded_credentials}
```

#### Получить прогресс за диапазон дат
```http
GET /daily-progress/character/{character_id}/date-range/admin?start_date=2025-10-01T00:00:00&end_date=2025-10-31T23:59:59
Authorization: Basic {base64_encoded_credentials}
```

#### Получить прогресс по ID
```http
GET /daily-progress/{progress_id}/admin
Authorization: Basic {base64_encoded_credentials}
```

#### Создать прогресс
```http
POST /daily-progress/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "character_id": "uuid",
  "date": "2025-10-12T00:00:00Z",
  "experience_gained": 50,
  "mood_average": "happy",
  "behavior_index": 85
}
```

#### Обновить прогресс
```http
PATCH /daily-progress/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "progress_id": "uuid",
  "experience_gained": 75,
  "mood_average": "happy",
  "behavior_index": 90
}
```

#### Удалить прогресс
```http
DELETE /daily-progress/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "progress_id": "uuid"
}
```

---

## История настроения (Mood History)

### 😊 Получить историю настроения за день
```http
GET /mood-history/me?day=2025-10-12T00:00:00
Authorization: Bearer {telegram_init_data}
```

### 😊 Получить историю настроения за диапазон дат
```http
GET /mood-history/me?start_date=2025-10-01T00:00:00&end_date=2025-10-31T23:59:59
Authorization: Bearer {telegram_init_data}
```

**Response:**
```json
[
  {
    "id": "uuid",
    "character_id": "uuid",
    "mood": "happy",
    "trigger": "exercise",
    "timestamp": "2025-10-12T12:00:00Z"
  }
]
```

**Примечание:** `mood` может быть: `neutral`, `happy`, `sad`, `angry`, `bored`.

### ➕ Добавить запись о настроении
```http
POST /mood-history/me
Authorization: Bearer {telegram_init_data}
Content-Type: application/json

{
  "mood": "happy",
  "trigger": "exercise"
}
```

### 🔧 Админские эндпоинты

#### Список истории настроения для персонажа
```http
GET /mood-history/admin?character_id={uuid}&limit=100
Authorization: Basic {base64_encoded_credentials}
```

#### Получить запись о настроении по ID
```http
GET /mood-history/{mood_history_id}/admin
Authorization: Basic {base64_encoded_credentials}
```

#### Создать запись о настроении
```http
POST /mood-history/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "character_id": "uuid",
  "mood": "happy",
  "trigger": "exercise"
}
```

#### Обновить запись о настроении
```http
PATCH /mood-history/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "mood_history_id": "uuid",
  "mood": "sad",
  "trigger": "updated trigger"
}
```

#### Удалить запись о настроении
```http
DELETE /mood-history/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "mood_history_id": "uuid"
}
```

---

## Транзакции (Transactions)

### 💳 Получить свои транзакции
```http
GET /transactions/me
Authorization: Bearer {telegram_init_data}
```

### 💳 Получить свои транзакции с фильтрацией
```http
GET /transactions/me?start_date=2025-10-01T00:00:00&end_date=2025-10-31T23:59:59&transaction_type=deposit
Authorization: Bearer {telegram_init_data}
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

### 🔧 Админские эндпоинты

#### Список транзакций
```http
GET /transactions/admin?limit=100&offset=0
Authorization: Basic {base64_encoded_credentials}
```

#### Получить транзакцию по ID
```http
GET /transactions/{transaction_id}/admin
Authorization: Basic {base64_encoded_credentials}
```

#### Создать транзакцию
```http
POST /transactions/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "user_tg_id": 123456789,
  "amount": 100,
  "type": "deposit",
  "description": "Manual deposit"
}
```

#### Обновить транзакцию
```http
PATCH /transactions/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "transaction_id": "uuid",
  "amount": 150,
  "description": "Updated description"
}
```

#### Удалить транзакцию
```http
DELETE /transactions/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "transaction_id": "uuid"
}
```

---

## Друзья (User Friends)

### 👥 Получить список своих друзей
```http
GET /user-friends/me
Authorization: Bearer {telegram_init_data}
```

**Response:**
```json
[
  {
    "id": "uuid",
    "owner_tg_id": 123456789,
    "friend_tg_id": 987654321,
    "created_at": "2025-10-12T12:00:00Z"
  }
]
```

### ➕ Добавить друга
```http
POST /user-friends/me
Authorization: Bearer {telegram_init_data}
Content-Type: application/json

{
  "friend_tg_id": 987654321
}
```

**Ошибка при попытке добавить уже существующего друга:**
```json
{
  "detail": "This user is already in your friends list"
}
```

### 🗑️ Удалить друга
```http
DELETE /user-friends/me
Authorization: Bearer {telegram_init_data}
Content-Type: application/json

{
  "friend_tg_id": 987654321
}
```

### 👤 Получить полную информацию о друге
```http
GET /user-friends/me/friend?friend_tg_id=987654321
Authorization: Bearer {telegram_init_data}
```

**Примечание:** Требуется взаимная дружба (оба пользователя должны добавить друг друга).

**Response:**
```json
{
  "user_tg_id": 987654321,
  "character": {
    "id": "uuid",
    "name": "Friend Name",
    "sex": "male",
    "current_mood": "happy",
    "level": 5,
    "total_experience": 100
  },
  "character_items": [...],
  "character_backgrounds": [...],
  "base_activities": [...],
  "mood_history": [],
  "transactions": []
}
```

### 🔧 Админские эндпоинты

#### Список друзей пользователя
```http
GET /user-friends/{owner_tg_id}/admin
Authorization: Basic {base64_encoded_credentials}
```

#### Получить запись друга по ID
```http
GET /user-friends/id/{friend_id}/admin
Authorization: Basic {base64_encoded_credentials}
```

#### Добавить друга
```http
POST /user-friends/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "owner_tg_id": 123456789,
  "friend_tg_id": 987654321
}
```

#### Обновить запись друга
```http
PATCH /user-friends/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "friend_id": "uuid",
  "friend_tg_id": 987654322
}
```

#### Удалить друга
```http
DELETE /user-friends/admin
Authorization: Basic {base64_encoded_credentials}
Content-Type: application/json

{
  "owner_tg_id": 123456789,
  "friend_tg_id": 987654321
}
```

---

## Настройки пользователя (User Settings)

### ⚙️ Получить свои настройки
```http
GET /user-settings/me
Authorization: Bearer {telegram_init_data}
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
PATCH /user-settings/me
Authorization: Bearer {telegram_init_data}
Content-Type: application/json

{
  "quiet_start_time": "23:00:00",
  "quiet_end_time": "07:00:00",
  "muted_days": ["sunday"],
  "do_not_disturb": true
}
```

**Примечание:** Все поля опциональны, обновляются только переданные.

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
  "detail": "This user is already in your friends list"
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

**Дублирование сущности:**
```json
{
  "detail": "Entity already exists"
}
```

---

## Примечания

### 🔒 Безопасность
- Все пользовательские endpoints (`/me`) требуют Bearer Token авторизацию (Telegram Mini App Init Data)
- Все админские endpoints требуют Basic Authentication
- `telegram_id` извлекается из токена, не передается в body/query
- Пользователи могут управлять только своими данными
- Проверка владения ресурсами выполняется на стороне сервера

### 📝 Ограничения
- Пользователи могут создавать персонажей, указывая только `name` и `sex`
- Серверные поля (`level`, `experience`, `mood`) управляются автоматически
- Покупка проверяет баланс и доступность товара
- Все транзакции логируются
- Удаление категорий предметов невозможно, если есть связанные предметы
- Удаление типов активностей каскадно удаляет связанные активности

### 🌐 Открытые endpoints (без авторизации)
- `GET /items/catalog`
- `GET /backgrounds/catalog`
- `GET /activity-types/catalog`
- `GET /item-categories/catalog`

Эти endpoints доступны для всех и используются для отображения каталога в магазине.

### 🔄 Каскадное удаление
При удалении родительских сущностей автоматически удаляются связанные:
- При удалении `activity_type` удаляются связанные `base_character_activities` и `character_activity_history`
- При удалении `item` удаляются связанные `character_items`
- При удалении `background` удаляются связанные `character_backgrounds`

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
