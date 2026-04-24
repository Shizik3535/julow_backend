# 17. Localization — Локализация

## Обзор

Контекст локализации обеспечивает мультиязычный интерфейс, RTL-поддержку, локализованные форматы дат/чисел/валют и часовые пояса. Поддержка crowdsourced-переводов.

**Доступность:** Все тарифы ✅

---

## Принципы расширяемости

1. **Locale — AR** — конфигурация языка с форматами, направлением текста, процентом завершённости.
2. **TextDirection — enum** — `LTR`, `RTL`. Стабильное множество.
3. **TranslationStatus — enum** — `DRAFT`, `APPROVED`, `REJECTED`. Жизненный цикл перевода.
4. **Namespace** — строка с валидацией — группировка ключей по контекстам.
5. **Fallback chain** — user locale → language without region → English.
6. **Plural forms** — ICU plural rules (one, few, many, other).

---

## 1. Функциональные требования

### 1.1. Мультиязычность

| Требование | Описание |
|-----------|----------|
| Языки интерфейса | EN, RU, DE, FR, ES, PT, ZH, JA, KO + расширяемо |
| Fallback | Если перевод отсутствует → English |
| Определение языка | Автоопределение из браузера → настройки пользователя |
| Переключение языка | В реальном времени, без перезагрузки |
| RTL-поддержка | Арабский (ar), Иврит (he) |

### 1.2. Форматы

| Формат | Примеры |
|--------|---------|
| Дата | DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD |
| Время | 12h (AM/PM), 24h |
| Числа | 1,234.56 (EN), 1.234,56 (DE), 1 234,56 (RU) |
| Валюта | $100.00 (USD), 100,00 € (EUR), 100,00 ₽ (RUB) |
| Первый день недели | Monday (ISO) / Sunday (US) / Saturday (ME) |

### 1.3. Часовые пояса

- Автоопределение из браузера
- Ручной выбор (IANA timezone database)
- Все даты хранятся в UTC, отображаются в пользовательском TZ
- Дедлайны/события: учитывают TZ пользователя при создании

### 1.4. Crowdsourced Translations (🔮 Future)

- Платформа для сообщества переводчиков
- Голосование за переводы
- Ревью модераторами
- Автоматический импорт одобренных переводов

---

## 2. Доменная модель

### Value Objects

| VO | Тип | Описание |
|---|---|---|
| `TextDirection` | Enum | `LTR`, `RTL` |
| `TranslationStatus` | Enum | `DRAFT`, `APPROVED`, `REJECTED` |
| `LocaleCode` | frozen dataclass | code: str (ISO 639-1 + optional region, e.g. `en`, `ru`, `pt-BR`) |
| `NumberFormat` | frozen dataclass | decimal_separator: str, thousands_separator: str |
| `CurrencyFormat` | frozen dataclass | pattern: str (e.g. `"$#,##0.00"`) |

### Entities

| Сущность | Поля | Описание |
|---|---|---|
| `TranslationKey` | key: str (unique), namespace: str, description: str \| None, default_value: str | Ключ перевода |
| `Translation` | key_id: Id, locale_code: LocaleCode, value: str, status: TranslationStatus, translator_id: Id \| None, reviewer_id: Id \| None, reviewed_at \| None | Перевод |

### Aggregates

#### Locale (Aggregate Root)

Поля:
- code: LocaleCode (PK)
- name: str (English name)
- native_name: str
- direction: TextDirection
- date_format: str
- time_format: str
- number_format: NumberFormat
- currency_format: CurrencyFormat
- first_day_of_week: int (0=Mon, 6=Sun)
- is_enabled: bool
- completion_percentage: int (0–100)
- created_at: datetime
- updated_at: datetime

Методы:
- `create(code, name, native_name, direction, formats)` → `Locale` (factory, is_enabled=True)
- `enable()` / `disable()`
- `update_formats(date_format=None, time_format=None, number_format=None, currency_format=None)`
- `update_completion(percentage)`

Инварианты:
- English (en) всегда 100% complete, нельзя disable
- code уникален глобально

---

## 3. Бизнес-правила

1. **Default locale**: English (en) — всегда 100% complete
2. **Fallback chain**: user locale → language without region → English
3. **RTL**: при RTL-locale — CSS direction: rtl, зеркальные layouts
4. **Dates**: всегда хранятся в UTC; отображаются в TZ пользователя
5. **Server responses**: даты в ISO 8601 (UTC); клиент конвертирует
6. **Translation keys**: immutable после создания; значения обновляемы
7. **Crowdsourced**: переводы проходят ревью перед публикацией
8. **Namespace isolation**: каждый контекст имеет свой namespace
9. **Plural forms**: поддержка plural rules по ICU (one, few, many, other)
10. **Interpolation**: переменные в строках `{{variable_name}}`

---

## 4. API Endpoints

### 4.1. Locales

```
GET /api/v1/locales
```

**Response (200):**
```json
{
  "locales": [
    {
      "code": "en",
      "name": "English",
      "native_name": "English",
      "direction": "ltr",
      "completion_percentage": 100,
      "is_enabled": true
    },
    {
      "code": "ru",
      "name": "Russian",
      "native_name": "Русский",
      "direction": "ltr",
      "completion_percentage": 95,
      "is_enabled": true
    },
    {
      "code": "ar",
      "name": "Arabic",
      "native_name": "العربية",
      "direction": "rtl",
      "completion_percentage": 60,
      "is_enabled": true
    }
  ]
}
```

### 4.2. Translations (Client)

```
GET /api/v1/translations/{locale_code}
```

**Query params:** `namespace` (optional — для lazy loading)

**Response (200):**
```json
{
  "locale": "ru",
  "translations": {
    "common.save": "Сохранить",
    "common.cancel": "Отмена",
    "task.status.in_progress": "В работе",
    "task.priority.high": "Высокий"
  },
  "version": "2025-02-01T10:00:00Z"
}
```

---

```
GET /api/v1/translations/{locale_code}/version
```
*Для проверки необходимости обновления кеша на клиенте*

**Response (200):**
```json
{
  "version": "2025-02-01T10:00:00Z"
}
```

### 4.3. Timezones

```
GET /api/v1/timezones
```

**Response (200):**
```json
{
  "timezones": [
    {"id": "Europe/Moscow", "name": "Moscow (UTC+3)", "offset": "+03:00"},
    {"id": "America/New_York", "name": "New York (UTC-5)", "offset": "-05:00"}
  ]
}
```

### 4.4. Admin: Translations Management

```
GET /api/v1/admin/translations/keys
```

**Query params:** `namespace`, `search`, `missing_locale`, `page`, `limit`

---

```
POST /api/v1/admin/translations/keys
```

---

```
GET /api/v1/admin/translations/keys/{key_id}/translations
```

---

```
PUT /api/v1/admin/translations/keys/{key_id}/translations/{locale_code}
```

**Request:**
```json
{
  "value": "Переведённая строка",
  "status": "approved"
}
```

---

```
POST /api/v1/admin/translations/import
```
*Массовый импорт переводов (JSON file)*

---

```
GET /api/v1/admin/translations/export/{locale_code}
```
*Экспорт всех переводов для locale*

---

```
GET /api/v1/admin/translations/stats
```

**Response (200):**
```json
{
  "total_keys": 1500,
  "locales": [
    {"code": "en", "translated": 1500, "percentage": 100},
    {"code": "ru", "translated": 1425, "percentage": 95},
    {"code": "de", "translated": 1200, "percentage": 80}
  ]
}
```

---

## 5. Схема БД

### Таблица: `locales`

| Колонка | Тип | Constraints |
|---------|-----|-------------|
| code | VARCHAR(10) | PK |
| name | VARCHAR(50) | NOT NULL |
| native_name | VARCHAR(50) | NOT NULL |
| direction | VARCHAR(3) | NOT NULL, DEFAULT 'ltr' |
| date_format | VARCHAR(15) | NOT NULL |
| time_format | VARCHAR(5) | NOT NULL |
| number_decimal_separator | VARCHAR(1) | NOT NULL, DEFAULT '.' |
| number_thousands_separator | VARCHAR(1) | NOT NULL, DEFAULT ',' |
| currency_format | VARCHAR(20) | NOT NULL |
| first_day_of_week | INTEGER | NOT NULL, DEFAULT 0 |
| is_enabled | BOOLEAN | NOT NULL, DEFAULT TRUE |
| completion_percentage | INTEGER | NOT NULL, DEFAULT 0 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

### Таблица: `translation_keys`

| Колонка | Тип | Constraints |
|---------|-----|-------------|
| id | UUID | PK |
| key | VARCHAR(200) | UNIQUE, NOT NULL |
| namespace | VARCHAR(50) | NOT NULL |
| description | TEXT | NULLABLE |
| default_value | TEXT | NOT NULL |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

**Индексы:**
- `idx_tk_namespace` — на `namespace`
- `idx_tk_key` — UNIQUE на `key`

### Таблица: `translations`

| Колонка | Тип | Constraints |
|---------|-----|-------------|
| id | UUID | PK |
| key_id | UUID | FK → translation_keys.id, NOT NULL |
| locale_code | VARCHAR(10) | FK → locales.code, NOT NULL |
| value | TEXT | NOT NULL |
| status | VARCHAR(10) | NOT NULL, DEFAULT 'draft' |
| translator_id | UUID | FK → users.id, NULLABLE |
| reviewer_id | UUID | FK → users.id, NULLABLE |
| reviewed_at | TIMESTAMPTZ | NULLABLE |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

**Индексы:**
- `idx_t_key_locale` — UNIQUE на `(key_id, locale_code)`
- `idx_t_locale` — на `locale_code`
- `idx_t_status` — на `status`

---

## 6. Доменные события

| Событие | Поля | Описание |
|---|---|---|
| `LocaleEnabled` | locale_code | Локаль включена |
| `LocaleDisabled` | locale_code | Локаль выключена |
| `TranslationKeyCreated` | key_id, key, namespace | Ключ создан |
| `TranslationUpdated` | key_id, locale_code | Перевод обновлён |
| `TranslationApproved` | key_id, locale_code, reviewer_id | Перевод одобрен |
| `TranslationRejected` | key_id, locale_code, reviewer_id | Перевод отклонён |
| `TranslationsImported` | locale_code, count | Переводы импортированы |
| `LocaleCompletionChanged` | locale_code, old_percentage, new_percentage | Процент изменился |

---

## 7. Exceptions

| Исключение | Описание |
|---|---|
| `LocaleNotFoundException` | Локаль не найдена |
| `CannotDisableDefaultLocaleException` | English нельзя выключить |
| `DuplicateTranslationKeyException` | Ключ уже существует |
| `TranslationNotFoundException` | Перевод не найден |
| `InvalidLocaleCodeException` | Некорректный код локали |

---

## 8. Repositories

| Репозиторий | Методы |
|---|---|
| `LocaleRepository` | `get_by_code`, `get_all`, `get_enabled` |
| `TranslationKeyRepository` | `get_by_id`, `get_by_key`, `get_by_namespace`, `get_missing_for_locale`, `search` |
| `TranslationRepository` | `get_by_key_and_locale`, `get_all_for_locale`, `get_by_status`, `get_by_namespace_and_locale` |
