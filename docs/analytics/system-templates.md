# Системные шаблоны дашбордов

Analytics BC поставляет набор глобальных (`is_system=True`,
`workspace_id IS NULL`) шаблонов дашбордов. Они доступны во всех
workspace и используются для быстрого создания персональных дашбордов
через `POST /dashboards/from-template`.

Source of truth — `app/context/analytics/infrastructure/persistence/seed/system_dashboard_templates.py`.
Сидинг выполняется alembic-миграцией `seed_system_dashboard_templates`
и/или скриптом `python -m scripts.seed_dashboard_templates`
(идемпотентно, ON CONFLICT по стабильным UUID).

## Состав

| Шаблон | UUID | Виджеты |
|---|---|---|
| **Project Overview** | `00000000-0000-0000-0007-000000000001` | Всего задач (NUMBER), Задачи по статусу (PIE), Топ-10 исполнителей (BAR), Прогресс проектов (TABLE) |
| **Task Analytics** | `00000000-0000-0000-0007-000000000002` | Открытые задачи (NUMBER), Приоритеты (PIE), Типы (BAR), Создание задач по дням (LINE) |
| **Time Tracking** | `00000000-0000-0000-0007-000000000003` | Всего отработано сек (NUMBER), Часы по пользователям (BAR), Часы по категориям (BAR), Часы по дням (LINE) |

## Использование

```http
POST /api/v1/dashboards/from-template
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "template_id": "00000000-0000-0000-0007-000000000001",
  "workspace_id": "<uuid>",
  "name": "My Project Overview"
}
```

Шаблоны клонируются по значению: дальнейшие изменения шаблона **не**
распространяются на ранее созданные дашборды.

## Запуск сидинга

```bash
# В рамках обычного миграционного процесса:
alembic upgrade head

# Standalone (например, для интеграционных тестов):
python -m scripts.seed_dashboard_templates
```

## Расширение

Чтобы добавить новый системный шаблон:

1. Добавить запись в `SYSTEM_DASHBOARD_TEMPLATES` со **стабильным** UUID
   (для идемпотентности сидинга).
2. Все используемые `DataSource` должны быть зарегистрированы в
   соответствующем resolver'е
   (`infrastructure/query_execution/resolvers/*`).
3. Добавить новую alembic-миграцию, импортирующую только новые записи
   (или создать миграцию `update_system_dashboard_templates` с
   ON CONFLICT по id).
4. Обновить unit-тесты в `tests/unit/analytics/`.

## Связанные эндпоинты

- `GET /api/v1/dashboard-templates` — список (system + workspace).
- `POST /api/v1/dashboards/from-template` — создать дашборд из шаблона.
- `GET /api/v1/analytics/schema` — метаданные `DataSource` для построения
  собственных шаблонов.
