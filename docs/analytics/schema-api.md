# Analytics Schema API

Эндпоинты для интроспекции аналитического движка: какие `DataSource`
доступны, какие поля у каждого источника, какие операторы / агрегации /
гранулярности существуют.

Все эндпоинты доступны под `/api/v1/analytics/` и требуют только JWT-
аутентификации (это метаданные движка, не клиентские данные).

## Эндпоинты

### GET /analytics/schema

Полный реестр.

```http
GET /api/v1/analytics/schema
Authorization: Bearer <jwt>
```

Ответ (сокращённо):

```json
{
  "success": true,
  "data": {
    "data_sources": [
      {
        "data_source": "tasks",
        "bounded_context": "task",
        "description": "Агрегация задач Task BC ...",
        "fields": [
          { "name": "project_id", "type": "uuid", "filterable": true, "groupable": true, "sortable": true, ... },
          { "name": "status", "type": "enum", "allowed_values": ["active", "archived"], ... },
          { "name": "created_at", "type": "datetime", "time_granularity_supported": true, ... }
        ],
        "supported_aggregations": ["count", "count_distinct"],
        "default_metrics": [{"field": "*", "aggregation": "count", "alias": "count"}]
      }
    ],
    "filter_operators": ["eq", "neq", "gt", "gte", "lt", "lte", "in", "not_in", "contains", "starts_with", "is_null", "is_not_null", "between"],
    "aggregations": ["count", "count_distinct", "sum", "avg", "min", "max", "median", "p90", "p95", "p99", "rate"],
    "time_granularities": ["hour", "day", "week", "month", "quarter", "year"],
    "sort_orders": ["asc", "desc"],
    "widget_types": ["pie_chart", "line_chart", "bar_chart", "number", "table", "list", "burndown_chart", "cumulative_flow", "heatmap", "gauge", "kanban_board", "scatter_plot", "histogram"]
  }
}
```

### GET /analytics/data-sources

Краткий список источников (без полей).

```json
{
  "success": true,
  "data": [
    { "data_source": "tasks", "bounded_context": "task", "description": "..." },
    { "data_source": "time_entries", "bounded_context": "timetracking", "description": "..." }
  ]
}
```

### GET /analytics/data-sources/{data_source}

Полная схема одного источника. Возвращает **404**, если источник не
известен движку (нет резолвера) либо не существует в `DataSource` enum.

```http
GET /api/v1/analytics/data-sources/tasks
```

## Семантика полей

| Поле дескриптора | Назначение |
|---|---|
| `name` | Канонический ключ, который клиент кладёт в `FilterConfig.field` / `Dimension.field` / `SortConfig.field`. |
| `type` | `string` \| `uuid` \| `enum` \| `datetime` \| `date` \| `integer` \| `float` \| `boolean`. |
| `filterable` | Можно использовать в `AnalyticsQuery.filters`. |
| `groupable` | Можно использовать в `AnalyticsQuery.dimensions` (`group_by`). |
| `sortable` | Можно использовать в `AnalyticsQuery.sort`. |
| `time_granularity_supported` | Поле — datetime/date-измерение; для него допустимо указать `time_granularity`. |
| `allowed_values` | Для `type='enum'` — список валидных значений. |
| `notes` | Особенности (например, "обязательный фильтр" или "игнорируется"). |

## Пример: построить запрос на основе схемы

1. `GET /analytics/data-sources` — выбрать `data_source` (например, `tasks`).
2. `GET /analytics/data-sources/tasks` — увидеть, что `assignee_id`
   `groupable=True`, а `count` — поддержанная агрегация.
3. Сформировать `AnalyticsQuery`:

```json
{
  "data_source": "tasks",
  "metrics": [{"field": "*", "aggregation": "count", "alias": "count"}],
  "dimensions": [{"field": "assignee_id", "alias": "assignee"}],
  "sort": [{"field": "count", "order": "desc"}],
  "limit": 10
}
```

4. `POST /analytics/execute?workspace_id=...` с этим query.

## Поддерживаемые DataSource (на момент написания)

`tasks`, `task_status_history`, `sprints`, `sprint_burndown`,
`sprint_velocity`, `projects`, `project_progress`, `time_entries`,
`workload`, `workspaces`.

Остальные значения `DataSource` enum (`comments`, `files`,
`notifications`, ...) пока не имеют резолверов — `/data-sources/{...}`
вернёт **404** для них.

## Реализация

- **Application port**: `AnalyticsSchemaPort`
  (`app/context/analytics/application/ports/schema/`).
- **Static adapter**: `StaticAnalyticsSchemaAdapter`
  (`app/context/analytics/infrastructure/schema/`). Зеркалит знание
  резолверов о cross-BC полях. Расхождения ловятся unit-тестами в
  `tests/unit/analytics/test_static_analytics_schema_adapter.py`.
- **Controller**: `AnalyticsSchemaController`
  (`app/context/analytics/presentation/controllers/`).

Чтобы добавить поддержку нового `DataSource`:

1. Реализовать resolver в `infrastructure/query_execution/resolvers/`.
2. Зарегистрировать его в DI-контейнере
   (`analytics_query_executor_port.resolvers`).
3. Добавить запись в `_DATA_SOURCE_SCHEMAS`
   (`StaticAnalyticsSchemaAdapter`).
4. Дополнить unit-тест `_RESOLVER_SUPPORTED`.
