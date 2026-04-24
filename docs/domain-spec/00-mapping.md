# Маппинг требований → Bounded Contexts

Исходные разделы требований распределены по BC следующим образом:

| Раздел | BC | Путь |
|---|---|---|
| 1. Аутентификация и авторизация | **Identity** | `app/context/identity/domain` |
| 2. Системные роли | **Identity** (shared) | `app/shared/domain` |
| 3. Организации | **Organization** | `app/context/organization/domain` |
| 4. Workspace | **Workspace** | `app/context/workspace/domain` |
| 5. Проекты | **Project** | `app/context/project/domain` |
| 6. Задачи | **Task** | `app/context/task/domain` |
| 7. Комментарии и коммуникация | **Communication** | `app/context/communication/domain` |
| 8. Файлы и документы | **FileStorage** | `app/context/filestorage/domain` |
| 9. Учёт времени | **TimeTracking** | `app/context/timetracking/domain` |
| 10. Уведомления | **Notification** | `app/context/notification/domain` |
| 11. Отчётность и аналитика | **Analytics** | `app/context/analytics/domain` |
| 12. Импорт / Экспорт | **ImportExport** | `app/context/importexport/domain` |
| 13. Персонализация | **Profile** | `app/context/profile/domain` |
| 14. Безопасность | **Security** | `app/context/security/domain` |
| 15. Администрирование | **Administration** | `app/context/administration/domain` |
| 16. Поддержка пользователей | **Support** | `app/context/support/domain` |
| 17. Локализация | **Profile** (настройки) + shared kernel | cross-cutting |
| 18. Фильтрация, сортировка, поиск | Application layer (не доменный) | — |
| 19. Биллинг и оплата | **Billing** | `app/context/billing/domain` |

## Правила BC

1. **Доменный слой изолирован** — BC не импортирует другой BC на уровне `domain/`
2. **Ссылки через opaque ID** — только `Id` или `str` для ссылок на другие BC
3. **Взаимодействие через events** — на application/infrastructure слоях
4. **ACL** — трансляция моделей между BC на application слое

## Правила `__init__.py`

1. Каждый подмодуль (`value_objects/`, `entities/`, `events/`, `exceptions/`, `aggregates/`, `repositories/`) имеет свой `__init__.py` с явными импортами и `__all__`
2. `domain/__init__.py` реэкспортирует всё из подмодулей — но **не импортирует из другого BC**
3. Импорты внутри BC только по абсолютным путям от корня проекта (`app.context.<bc>.domain...`)
4. Shared kernel импортируется через `app.shared.domain...`

## Структура каталогов каждого BC

```
app/context/<bc>/domain/
├── __init__.py              # реэкспорт всего
├── value_objects/
│   ├── __init__.py
│   └── <vo_name>.py         # один файл = один VO
├── entities/
│   ├── __init__.py
│   └── <entity_name>.py     # один файл = одна сущность
├── events/
│   ├── __init__.py
│   └── <aggregate>_events.py   # события по агрегатам (один файл = один агрегат)
├── exceptions/
│   ├── __init__.py
│   └── <aggregate>_exceptions.py   # исключения по агрегатам (один файл = один агрегат)
├── aggregates/
│   ├── __init__.py
│   └── <aggregate_name>.py  # один файл = один агрегат
└── repositories/
    ├── __init__.py
    └── <aggregate_name>_repository.py  # один файл = один репозиторий
```

## Порядок реализации

1. Identity (уже существует)
2. Profile
3. Organization
4. Workspace
5. Project
6. Task
7. Communication
8. FileStorage
9. TimeTracking
10. Notification
11. Analytics
12. Billing
13. Security
14. Administration
15. ImportExport
16. Support
