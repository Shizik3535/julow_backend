# 13. Personalization — Персонализация

## Обзор

Контекст персонализации управляет профилем пользователя, пользовательскими настройками интерфейса (тема, формат, плотность), горячими клавишами и индивидуальными предпочтениями.

**Доступность:** Все тарифы ✅ (с вариациями)

---

## Принципы расширяемости

1. **Стабильные множества — enum, расширяемые — string с валидацией** — `Theme`, `TimeFormat`, `InterfaceDensity`, `WeekStartDay` стабильны → enum. `StartPage`, `DateFormat` будут расти → string с паттерном.
2. **Настройки сгруппированы в VO** — вместо N полей на AR — VO-группы: AppearanceSettings, LocalizationSettings, NavigationSettings, NotificationSettings, PrivacySettings.
3. **Нет UserStatus** — статус аккаунта принадлежит Identity BC.
4. **Типизированные ссылки** — `PinnedTargetType` enum, `HotkeyAction` enum.
5. **Events по группам** — одно событие на группу настроек, с `changed_fields`.

---

## 1. Функциональные требования

### 1.1. Профиль

| Поле | Описание | Все тарифы |
|------|----------|-----------|
| Аватар | PNG/JPG, до 2 MB, crop to 256×256 | ✅ |
| Имя (display_name) | 2–100 символов | ✅ |
| Должность (job_title) | до 100 символов | ✅ |
| Часовой пояс | IANA timezone | ✅ |
| Язык интерфейса | ISO 639-1 (en, ru, de, ...) | ✅ |
| Телефон | optional, E.164 format | ✅ |
| Bio / О себе | до 500 символов | ✅ |

### 1.2. Настройки интерфейса

| Настройка | Варианты | Все тарифы |
|-----------|----------|-----------|
| Тема | Light, Dark, System, Custom (Enterprise) | ✅ |
| Формат даты | DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD | ✅ |
| Формат времени | 12h, 24h | ✅ |
| Первый день недели | Monday, Sunday, Saturday | ✅ |
| Стартовая страница | My Tasks, Dashboard, Inbox, Last Visited | ✅ |
| Плотность интерфейса | Compact, Comfortable, Spacious | ✅ |
| Accent color | HEX | ✅ |
| Sidebar | порядок проектов, избранное | ✅ |
| Горячие клавиши | Просмотр и кастомизация | ✅ |

### 1.3. Избранное и закрепление

- Закрепление workspace (pin)
- Закрепление проекта (pin)
- Закрепление задачи (pin / star)
- Избранные фильтры (saved filters)
- Порядок элементов в sidebar (drag-n-drop)

---

## 2. Доменная модель

### Value Objects

| VO | Тип | Описание |
|---|---|---|
| `Theme` | Enum | `LIGHT`, `DARK`, `SYSTEM`, `CUSTOM` |
| `InterfaceDensity` | Enum | `COMPACT`, `COMFORTABLE`, `SPACIOUS` |
| `TimeFormat` | Enum | `H24`, `H12` |
| `WeekStartDay` | Enum | `MONDAY`, `SUNDAY`, `SATURDAY` |
| `DateFormat` | str (validated) | Паттерн: `"DD.MM.YYYY"`, `"MM/DD/YYYY"`, `"YYYY-MM-DD"`, etc. |
| `StartPage` | str (validated) | `"my_tasks"`, `"dashboard"`, `"inbox"`, `"calendar"`, `"reports"` |
| `AccentColor` | frozen dataclass | hex: str (validated `#RRGGBB`) |
| `CustomTheme` | frozen dataclass | name: str, colors: dict[str, AccentColor] |
| `PinnedTargetType` | Enum | `WORKSPACE`, `PROJECT`, `TASK`, `DASHBOARD`, `REPORT` |
| `HotkeyAction` | Enum | `CREATE_TASK`, `NAVIGATE_INBOX`, `SEARCH`, `TOGGLE_SIDEBAR`, `GO_HOME`, `QUICK_ACTION` |
| `HotkeyConfig` | frozen dataclass | action: HotkeyAction, key_combination: str, is_enabled: bool |
| `SidebarSection` | frozen dataclass | section_id: str, is_collapsed: bool, item_ids: list[Id], order: int |
| `ProfileVisibility` | Enum | `PUBLIC`, `ORGANIZATION_ONLY`, `PRIVATE` |
| `OnlineStatusVisibility` | Enum | `EVERYONE`, `CONTACTS_ONLY`, `NOBODY` |
| `ActivityTrackingConsent` | Enum | `GRANTED`, `DENIED` |

> **`DateFormat` как string** — форматов дат много (локали). Валидация через regex.
>
> **`StartPage` как string** — новые разделы появляются часто, проверка на app-слое.

#### VO Groups

**AppearanceSettings**: theme, accent_color, custom_theme: CustomTheme | None, interface_density

**LocalizationSettings**: language: LanguageCode, timezone: Timezone, date_format, time_format, week_start_day

**NavigationSettings**: start_page

**PrivacySettings**: profile_visibility, online_status_visibility, activity_tracking_consent

### Entities

| Сущность | Поля | Описание |
|---|---|---|
| `PinnedItem` | target_type: PinnedTargetType, target_id: Id, order: int, pinned_at | Закреплённый элемент |
| `SocialLink` | platform: str, url: Url, display_name: str \| None | Социальная ссылка |

### Aggregates

#### UserProfile (Aggregate Root)

Один AR на пользователя. Настройки организованы в VO-группы.

Поля:
- user_id: Id (opaque, из Identity BC)
- avatar_url: Url | None
- display_name: str
- bio: str | None
- job_title: str | None
- phone: str | None
- social_links: list[SocialLink]
- appearance: AppearanceSettings
- localization: LocalizationSettings
- navigation: NavigationSettings
- privacy: PrivacySettings
- hotkeys: list[HotkeyConfig]
- sidebar_sections: list[SidebarSection]
- pinned_items: list[PinnedItem]
- created_at: datetime
- updated_at: datetime

Методы:
- `create(user_id)` → `UserProfile` (factory, дефолтные настройки)
- `change_avatar(url)` / `remove_avatar()`
- `update_personal_info(display_name=None, bio=None, job_title=None, phone=None)`
- `add_social_link(platform, url, display_name=None)` / `remove_social_link(platform)`
- `update_appearance(settings: AppearanceSettings)`
- `update_localization(settings: LocalizationSettings)`
- `update_navigation(settings: NavigationSettings)`
- `update_privacy(settings: PrivacySettings)`
- `update_hotkeys(configs: list[HotkeyConfig])`
- `update_sidebar(sections: list[SidebarSection])`
- `pin_item(target_type, target_id)` / `unpin_item(target_type, target_id)`
- `reorder_pinned_items(ordered_ids: list[Id])`

Инварианты:
- Один пользователь — один профиль
- Pinned items уникальны по (target_type, target_id)
- Social links уникальны по platform
- Custom theme доступен только для Enterprise
- Максимум 50 pinned items

#### Значения по умолчанию

| Группа | Значения |
|---|---|
| AppearanceSettings | theme=SYSTEM, accent_color=#6366F1, density=COMFORTABLE |
| LocalizationSettings | language=en, timezone=UTC, date_format=YYYY-MM-DD, time_format=H24, week_start_day=MONDAY |
| NavigationSettings | start_page=dashboard |
| PrivacySettings | profile_visibility=ORGANIZATION_ONLY, online_status=EVERYONE, activity_tracking=GRANTED |

---

## 3. Бизнес-правила

1. **Profile**: display_name обязателен, остальное опционально
2. **Avatar**: загружается через File Management, crop/resize до 256×256 на сервере
3. **Timezone**: используется для отображения дат и уведомлений
4. **Locale**: определяет язык интерфейса и форматы
5. **Custom theme**: доступен только для Enterprise
6. **Sidebar order**: хранится как массив {type, id}, отображается в порядке массива
7. **Keyboard shortcuts**: хранятся только override'ы (отличия от дефолтных)
8. **Pins**: максимум 50 pinned items на пользователя
9. **Settings defaults**: при создании пользователя — дефолтные настройки из системы
10. **Accent color**: применяется к UI-элементам (кнопки, ссылки, индикаторы)

---

## 4. API Endpoints

### 4.1. Профиль

```
GET /api/v1/users/me/profile
```

---

```
PATCH /api/v1/users/me/profile
```

**Request:**
```json
{
  "display_name": "John Doe",
  "job_title": "Senior Developer",
  "timezone": "Europe/Moscow",
  "locale": "ru",
  "bio": "Backend developer, coffee enthusiast"
}
```

---

```
PUT /api/v1/users/me/profile/avatar
```

**Request (multipart/form-data):**
- `avatar` — image file

---

```
DELETE /api/v1/users/me/profile/avatar
```

---

```
GET /api/v1/users/{user_id}/profile
```
*Публичный профиль (видимые поля)*

### 4.2. Настройки

```
GET /api/v1/users/me/settings
```

**Response (200):**
```json
{
  "theme": "dark",
  "date_format": "DD/MM/YYYY",
  "time_format": "24h",
  "first_day_of_week": 0,
  "start_page": "my_tasks",
  "density": "comfortable",
  "accent_color": "#3498DB",
  "sidebar_order": [
    {"type": "workspace", "id": "uuid1"},
    {"type": "project", "id": "uuid2"}
  ]
}
```

---

```
PATCH /api/v1/users/me/settings
```

**Request:**
```json
{
  "theme": "dark",
  "density": "compact",
  "accent_color": "#E74C3C"
}
```

### 4.3. Горячие клавиши

```
GET /api/v1/users/me/settings/keyboard-shortcuts
```

**Response (200):**
```json
{
  "defaults": {
    "new_task": "Ctrl+N",
    "search": "Ctrl+K",
    "save": "Ctrl+S",
    "toggle_sidebar": "Ctrl+B"
  },
  "overrides": {
    "new_task": "Ctrl+Shift+T"
  }
}
```

---

```
PATCH /api/v1/users/me/settings/keyboard-shortcuts
```

**Request:**
```json
{
  "overrides": {
    "new_task": "Ctrl+Shift+T",
    "search": "Ctrl+P"
  }
}
```

---

```
DELETE /api/v1/users/me/settings/keyboard-shortcuts
```
*Reset to defaults*

### 4.4. Pins

```
GET /api/v1/users/me/pins
```

---

```
POST /api/v1/users/me/pins
```

**Request:**
```json
{
  "target_type": "project",
  "target_id": "project_uuid"
}
```

---

```
DELETE /api/v1/users/me/pins/{pin_id}
```

---

```
PUT /api/v1/users/me/pins/reorder
```

**Request:**
```json
{
  "pin_ids": ["uuid1", "uuid3", "uuid2"]
}
```

---

## 5. Схема БД

### Таблица: `user_profiles`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| user_id | UUID | PK, FK → users.id | |
| avatar_url | VARCHAR(500) | NULLABLE | |
| display_name | VARCHAR(100) | NOT NULL | |
| job_title | VARCHAR(100) | NULLABLE | |
| phone | VARCHAR(20) | NULLABLE | E.164 |
| bio | VARCHAR(500) | NULLABLE | |
| timezone | VARCHAR(50) | NOT NULL, DEFAULT 'UTC' | |
| locale | VARCHAR(10) | NOT NULL, DEFAULT 'en' | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

### Таблица: `user_settings`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| user_id | UUID | PK, FK → users.id | |
| theme | VARCHAR(10) | NOT NULL, DEFAULT 'system' | |
| custom_theme | JSONB | NULLABLE | |
| date_format | VARCHAR(15) | NOT NULL, DEFAULT 'YYYY-MM-DD' | |
| time_format | VARCHAR(5) | NOT NULL, DEFAULT '24h' | |
| first_day_of_week | INTEGER | NOT NULL, DEFAULT 0 | 0=Mon |
| start_page | VARCHAR(20) | NOT NULL, DEFAULT 'my_tasks' | |
| density | VARCHAR(15) | NOT NULL, DEFAULT 'comfortable' | |
| accent_color | VARCHAR(7) | NULLABLE | |
| sidebar_order | JSONB | NOT NULL, DEFAULT '[]' | |
| keyboard_shortcuts | JSONB | NOT NULL, DEFAULT '{}' | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

### Таблица: `user_pins`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| user_id | UUID | FK → users.id, NOT NULL | |
| target_type | VARCHAR(20) | NOT NULL | |
| target_id | UUID | NOT NULL | |
| position | INTEGER | NOT NULL, DEFAULT 0 | |
| pinned_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_pin_user` — на `user_id`
- `idx_pin_user_target` — UNIQUE на `(user_id, target_type, target_id)`

---

## 6. Доменные события

| Событие | Поля | Описание |
|---|---|---|
| `ProfileCreated` | user_id | Профиль создан (по UserRegistered) |
| `ProfileDeleted` | user_id | Профиль удалён |
| `AppearanceSettingsChanged` | user_id, changed_fields: list[str] | Внешний вид изменён |
| `LocalizationSettingsChanged` | user_id, changed_fields: list[str] | Локализация изменена |
| `NavigationSettingsChanged` | user_id, changed_fields: list[str] | Навигация изменена |
| `PrivacySettingsChanged` | user_id, changed_fields: list[str] | Приватность изменена |
| `AvatarChanged` | user_id | Аватар изменён |
| `PersonalInfoChanged` | user_id, changed_fields: list[str] | Персональные данные |
| `HotkeysChanged` | user_id | Горячие клавиши |
| `PinnedItemAdded` | user_id, target_type, target_id | Закреплено |
| `PinnedItemRemoved` | user_id, target_type, target_id | Откреплено |
| `SidebarConfigUpdated` | user_id | Sidebar обновлён |

> **`changed_fields`** — список изменённых полей внутри группы. Добавление поля в VO-группу не требует нового event.

---

## 7. Exceptions

| Исключение | Описание |
|---|---|
| `ProfileNotFoundException` | Профиль не найден |
| `InvalidAccentColorException` | Некорректный формат цвета |
| `InvalidHotkeyException` | Некорректная комбинация / неизвестный action |
| `InvalidDateFormatException` | Некорректный паттерн формата даты |
| `InvalidStartPageException` | Некорректный идентификатор стартовой страницы |
| `DuplicatePinnedItemException` | Элемент уже закреплён |
| `DuplicateSocialLinkException` | Социальная ссылка уже существует |
| `InvalidUrlException` | Некорректный URL |

---

## 8. Repositories

| Репозиторий | Методы |
|---|---|
| `UserProfileRepository` | `get_by_user_id`, `get_by_id`, `search`, `get_by_role` |
