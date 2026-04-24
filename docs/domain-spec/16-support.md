# Support BC — Спецификация

> Путь: `app/context/support/domain`
> Исходные требования: §16 (Поддержка пользователей)

## Контекст

Support BC отвечает за help center, тикеты, чат поддержки, FAQ, changelog, status page. Это отдельный BC, так как поддержка имеет свою модель данных и бизнес-правила.

---

## Value Objects

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `TicketStatus` | Enum | `OPEN`, `IN_PROGRESS`, `WAITING_FOR_USER`, `RESOLVED`, `CLOSED` | §16.2 |
| `TicketPriority` | Enum | `LOW`, `MEDIUM`, `HIGH`, `URGENT` | §16.2 |
| `ArticleStatus` | Enum | `DRAFT`, `PUBLISHED`, `ARCHIVED` | §16.1 |
| `IncidentStatus` | Enum | `INVESTIGATING`, `IDENTIFIED`, `MONITORING`, `RESOLVED` | §16.1 |
| `CategoryType` | Enum | `GETTING_STARTED`, `TASKS`, `PROJECTS`, `BILLING`, `SECURITY`, `OTHER` | §16.1 |

## Entities

| Сущность | Поля | Описание | Исходное требование |
|---|---|---|---|
| `HelpArticle` | title: str, content: RichText, category: CategoryType, status: ArticleStatus, author_id: Id, views_count: int, created_at, updated_at | Статья help center | §16.1 |
| `FAQ` | question: str, answer: RichText, category: CategoryType, order: int | FAQ | §16.1 |
| `ChangelogEntry` | version: str, title: str, content: RichText, published_at: datetime | Запись changelog | §16.1 |
| `Incident` | title: str, status: IncidentStatus, started_at: datetime, resolved_at: datetime \| None, updates: list[dict] | Инцидент на status page | §16.1 |
| `TicketMessage` | sender_id: Id, content: RichText, is_internal: bool, created_at: datetime | Сообщение в тикете | §16.2 |

## Domain Events

| Событие | Поля | Описание | Исходное требование |
|---|---|---|---|
| `TicketCreated` | ticket_id, user_id, subject | Тикет создан | §16.2 |
| `TicketUpdated` | ticket_id | Тикет обновлён | §16.2 |
| `TicketMessageAdded` | ticket_id, sender_id | Сообщение добавлено | §16.2 |
| `TicketStatusChanged` | ticket_id, old_status, new_status | Статус тикета изменён | §16.2 |
| `TicketAssigned` | ticket_id, assignee_id | Тикет назначен | §16.2 |
| `TicketClosed` | ticket_id | Тикет закрыт | §16.2 |
| `HelpArticleCreated` | article_id | Статья создана | §16.1 |
| `HelpArticleUpdated` | article_id | Статья обновлена | §16.1 |
| `HelpArticlePublished` | article_id | Статья опубликована | §16.1 |
| `IncidentReported` | incident_id | Инцидент зарегистрирован | §16.1 |
| `IncidentUpdated` | incident_id | Обновление инцидента | §16.1 |
| `IncidentResolved` | incident_id | Инцидент решён | §16.1 |
| `ChangelogPublished` | entry_id | Changelog опубликован | §16.1 |

## Exceptions

| Исключение | Описание |
|---|---|
| `TicketNotFoundException` | Тикет не найден |
| `HelpArticleNotFoundException` | Статья не найдена |
| `IncidentNotFoundException` | Инцидент не найден |
| `CannotReopenTicketException` | Нельзя reopen тикет |
| `InvalidTicketTransitionException` | Некорректный переход статуса |

## Aggregates

### Ticket (Aggregate Root)

Поля:
- user_id: Id (автор тикета)
- subject: str
- status: TicketStatus
- priority: TicketPriority
- assignee_id: Id | None (support agent)
- messages: list[TicketMessage]
- workspace_id: Id | None (opaque)
- created_at, updated_at

Методы:
- `create(user_id, subject, priority)` → `Ticket` (factory)
- `add_message(sender_id, content, is_internal)`
- `change_status(new_status)`
- `assign(agent_id)`
- `close()`

Инварианты:
- Статус: OPEN → IN_PROGRESS → WAITING_FOR_USER → RESOLVED → CLOSED
- CLOSED тикет нельзя reopen
- Внутренние сообщения (is_internal) видны только support agent'ам

### HelpCenter (Aggregate Root) — опционально

Или можно сделать HelpArticle отдельным Aggregate Root.

### StatusPage (Aggregate Root) — опционально

Или Incident как отдельный Aggregate Root.

## Repositories

| Репозиторий | Методы |
|---|---|
| `TicketRepository` | `get_by_id`, `get_by_user`, `get_by_assignee`, `get_open_tickets` |
| `HelpArticleRepository` | `get_by_id`, `get_published`, `get_by_category`, `search` |
| `IncidentRepository` | `get_active`, `get_by_id` |
