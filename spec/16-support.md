# 16. Support — Поддержка пользователей

## Обзор

Контекст поддержки включает self-service ресурсы (Help Center, FAQ, Changelog) и прямую поддержку (чат, тикеты, email). Уровень поддержки зависит от тарифа.

---

## Принципы расширяемости

1. **TicketStatus — расширяемый enum** — `OPEN`, `WAITING_ON_SUPPORT`, `WAITING_ON_CUSTOMER`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`. Новые статусы = значение enum.
2. **TicketPriority — enum** — `LOW`, `MEDIUM`, `HIGH`, `URGENT`.
3. **ArticleStatus — enum** — `DRAFT`, `PUBLISHED`, `ARCHIVED`.
4. **IncidentStatus — enum** — `INVESTIGATING`, `IDENTIFIED`, `MONITORING`, `RESOLVED`.
5. **Ticket — AR** — тикет с полным жизненным циклом, SLA, назначением, оценкой.
6. **HelpArticle / FAQ / ChangelogEntry / Incident — entities** — независимые сущности self-service.

---

## 1. Функциональные требования

### 1.1. Self-Service

| Ресурс | Free | Start | Business | Enterprise |
|--------|------|-------|----------|------------|
| Help Center / Knowledge Base | ✅ | ✅ | ✅ | ✅ |
| FAQ | ✅ | ✅ | ✅ | ✅ |
| Видеотуториалы | ✅ | ✅ | ✅ | ✅ |
| Changelog / What's New | ✅ | ✅ | ✅ | ✅ |
| Status Page | ✅ | ✅ | ✅ | ✅ |
| Community Forum | ✅ | ✅ | ✅ | ✅ |
| API Documentation | ✅ | ✅ | ✅ | ✅ |

### 1.2. Прямая поддержка

| Канал | Free | Start | Business | Enterprise |
|-------|------|-------|----------|------------|
| Email-поддержка | ❌ | ✅ (48h SLA) | ✅ (24h SLA) | ✅ (4h SLA) |
| Чат поддержки (in-app) | ❌ | ❌ | ✅ (бизнес часы) | ✅ (24/7) |
| Тикет-система | ❌ | ✅ | ✅ | ✅ |
| Выделенный менеджер | ❌ | ❌ | ❌ | ✅ |
| Onboarding-сессия | ❌ | ❌ | ❌ | ✅ |
| Приоритетная поддержка | ❌ | ❌ | ❌ | ✅ |

---

## 2. Доменная модель

### Value Objects

| VO | Тип | Описание |
|---|---|---|
| `TicketStatus` | Enum | `OPEN`, `WAITING_ON_SUPPORT`, `WAITING_ON_CUSTOMER`, `IN_PROGRESS`, `RESOLVED`, `CLOSED` |
| `TicketPriority` | Enum | `LOW`, `MEDIUM`, `HIGH`, `URGENT` |
| `TicketCategory` | Enum | `BUG`, `FEATURE_REQUEST`, `QUESTION`, `BILLING`, `SECURITY`, `ACCOUNT`, `OTHER` |
| `ArticleStatus` | Enum | `DRAFT`, `PUBLISHED`, `ARCHIVED` |
| `IncidentStatus` | Enum | `INVESTIGATING`, `IDENTIFIED`, `MONITORING`, `RESOLVED` |
| `IncidentSeverity` | Enum | `MINOR`, `MAJOR`, `CRITICAL` |
| `SenderType` | Enum | `USER`, `SUPPORTER`, `SYSTEM` |
| `ChangelogType` | Enum | `FEATURE`, `IMPROVEMENT`, `BUGFIX`, `BREAKING` |
| `CategoryType` | Enum | `HELP`, `FAQ` |

### Entities

| Сущность | Поля | Описание |
|---|---|---|
| `HelpArticle` | category_id: Id, title, slug, content, locale, status: ArticleStatus, tags: list[str], views_count, helpful_count, not_helpful_count, author_id: Id, published_at \| None | Статья Help Center |
| `HelpCategory` | name, slug, description \| None, icon \| None, position, parent_category_id \| None, locale | Категория |
| `FAQ` | question, answer, category_id: Id, position, locale, is_published: bool | FAQ |
| `ChangelogEntry` | version, title, content, changelog_type: ChangelogType, published_at, created_by: Id | Запись changelog |
| `Incident` | title, status: IncidentStatus, severity: IncidentSeverity, affected_components: list[str], updates: list[IncidentUpdate], started_at, resolved_at \| None | Инцидент status page |
| `IncidentUpdate` | message, status: IncidentStatus, created_at | Обновление инцидента |
| `TicketMessage` | sender_id: Id, sender_type: SenderType, content, attachments: list[Id], is_internal: bool, created_at | Сообщение тикета |

### Aggregates

#### Ticket (Aggregate Root)

Поля:
- ticket_number: str (auto-generated, e.g. "TKT-0001")
- user_id: Id
- workspace_id: Id | None
- subject: str
- description: str
- category: TicketCategory
- priority: TicketPriority
- status: TicketStatus
- assigned_to: Id | None
- messages: list[TicketMessage]
- attachments: list[Id]
- sla_response_due: datetime | None
- sla_resolution_due: datetime | None
- first_response_at: datetime | None
- resolved_at: datetime | None
- satisfaction_rating: int | None (1-5)
- satisfaction_comment: str | None
- created_at: datetime
- updated_at: datetime
- closed_at: datetime | None

Методы:
- `create(user_id, subject, description, category, priority, workspace_id=None)` → `Ticket` (factory, status=OPEN)
- `assign(supporter_id)` → assigned_to
- `change_status(new_status)`
- `add_message(sender_id, sender_type, content, attachments=[], is_internal=False)`
- `resolve(resolved_by)` → status=RESOLVED
- `close()` → status=CLOSED
- `reopen()` → status=OPEN
- `set_satisfaction(rating, comment=None)`
- `check_sla_breach()` → bool

Инварианты:
- ticket_number глобально уникален
- Internal notes видны только команде поддержки
- Satisfaction запрашивается после RESOLVED/CLOSED
- SLA зависит от тарифа и приоритета
- Status transitions: OPEN → IN_PROGRESS/WAITING_ON_CUSTOMER → RESOLVED → CLOSED; CLOSED → OPEN (reopen)

---

## 3. Бизнес-правила

1. **SLA**: время ответа и решения зависит от тарифа и приоритета тикета
2. **Auto-assignment**: тикеты автоматически назначаются на свободного supporter'а (round-robin)
3. **Escalation**: если SLA нарушен → тикет эскалируется на Admin
4. **Satisfaction**: запрашивается после закрытия тикета (через 24 часа)
5. **Internal notes**: видны только команде поддержки
6. **Status Page**: публичная страница с текущим состоянием сервисов
7. **Changelog**: отображается в in-app "What's New" widget
8. **Help articles**: поддержка мультиязычности (locale)
9. **Ticket number**: глобально уникальный, auto-increment

---

## 4. API Endpoints

### 4.1. Help Center

```
GET /api/v1/help/categories
```

**Query params:** `locale`

---

```
GET /api/v1/help/articles
```

**Query params:** `category_id`, `locale`, `search`, `page`, `limit`

---

```
GET /api/v1/help/articles/{slug}
```

---

```
POST /api/v1/help/articles/{article_id}/feedback
```

**Request:**
```json
{
  "helpful": true
}
```

### 4.2. Тикеты (User)

```
GET /api/v1/support/tickets
```

**Query params:** `status`, `page`, `limit`

---

```
POST /api/v1/support/tickets
```

**Request:**
```json
{
  "subject": "Cannot export tasks",
  "description": "When I try to export...",
  "category": "bug",
  "priority": "medium",
  "workspace_id": "ws_uuid",
  "attachment_ids": ["file_uuid"]
}
```

---

```
GET /api/v1/support/tickets/{ticket_id}
```

---

```
POST /api/v1/support/tickets/{ticket_id}/messages
```

**Request:**
```json
{
  "content": "Here is the screenshot...",
  "attachment_ids": ["file_uuid"]
}
```

---

```
POST /api/v1/support/tickets/{ticket_id}/close
```

---

```
POST /api/v1/support/tickets/{ticket_id}/reopen
```

---

```
POST /api/v1/support/tickets/{ticket_id}/satisfaction
```

**Request:**
```json
{
  "rating": 5,
  "comment": "Great support!"
}
```

### 4.3. Тикеты (Admin/Supporter)

```
GET /api/v1/admin/support/tickets
```

**Query params:** `status`, `category`, `priority`, `assigned_to`, `page`, `limit`, `sort_by`

---

```
PUT /api/v1/admin/support/tickets/{ticket_id}/assign
```

**Request:**
```json
{
  "assigned_to": "supporter_uuid"
}
```

---

```
PUT /api/v1/admin/support/tickets/{ticket_id}/status
```

**Request:**
```json
{
  "status": "in_progress"
}
```

---

```
POST /api/v1/admin/support/tickets/{ticket_id}/messages
```

**Request:**
```json
{
  "content": "We've identified the issue...",
  "is_internal": false
}
```

### 4.4. Changelog

```
GET /api/v1/changelog
```

**Query params:** `type`, `page`, `limit`

---

```
POST /api/v1/admin/changelog
```
*(Admin only)*

---

```
PATCH /api/v1/admin/changelog/{entry_id}
```

### 4.5. Status Page

```
GET /api/v1/status
```
*Публичный endpoint*

**Response (200):**
```json
{
  "status": "operational",
  "components": [
    {"name": "API", "status": "operational"},
    {"name": "Web App", "status": "operational"},
    {"name": "File Storage", "status": "degraded_performance"}
  ],
  "active_incidents": [
    {
      "id": "uuid",
      "title": "Slow file uploads",
      "status": "monitoring",
      "severity": "minor",
      "started_at": "2025-02-01T10:00:00Z"
    }
  ]
}
```

---

## 5. Схема БД

### Таблица: `help_categories`

| Колонка | Тип | Constraints |
|---------|-----|-------------|
| id | UUID | PK |
| name | VARCHAR(100) | NOT NULL |
| slug | VARCHAR(100) | NOT NULL |
| description | TEXT | NULLABLE |
| icon | VARCHAR(100) | NULLABLE |
| position | INTEGER | NOT NULL, DEFAULT 0 |
| parent_category_id | UUID | FK → help_categories.id, NULLABLE |
| locale | VARCHAR(10) | NOT NULL, DEFAULT 'en' |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

### Таблица: `help_articles`

| Колонка | Тип | Constraints |
|---------|-----|-------------|
| id | UUID | PK |
| category_id | UUID | FK → help_categories.id, NOT NULL |
| title | VARCHAR(200) | NOT NULL |
| slug | VARCHAR(200) | NOT NULL |
| content | TEXT | NOT NULL |
| locale | VARCHAR(10) | NOT NULL, DEFAULT 'en' |
| status | VARCHAR(15) | NOT NULL, DEFAULT 'draft' |
| tags | JSONB | NOT NULL, DEFAULT '[]' |
| views_count | INTEGER | NOT NULL, DEFAULT 0 |
| helpful_count | INTEGER | NOT NULL, DEFAULT 0 |
| not_helpful_count | INTEGER | NOT NULL, DEFAULT 0 |
| author_id | UUID | FK → users.id, NOT NULL |
| published_at | TIMESTAMPTZ | NULLABLE |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

**Индексы:**
- `idx_ha_slug_locale` — UNIQUE на `(slug, locale)`
- `idx_ha_category` — на `category_id`
- `idx_ha_status` — на `status`

### Таблица: `support_tickets`

| Колонка | Тип | Constraints |
|---------|-----|-------------|
| id | UUID | PK |
| ticket_number | VARCHAR(20) | UNIQUE, NOT NULL |
| user_id | UUID | FK → users.id, NOT NULL |
| workspace_id | UUID | FK → workspaces.id, NULLABLE |
| subject | VARCHAR(200) | NOT NULL |
| description | TEXT | NOT NULL |
| category | VARCHAR(20) | NOT NULL |
| priority | VARCHAR(10) | NOT NULL, DEFAULT 'medium' |
| status | VARCHAR(25) | NOT NULL, DEFAULT 'open' |
| assigned_to | UUID | FK → users.id, NULLABLE |
| sla_response_due | TIMESTAMPTZ | NULLABLE |
| sla_resolution_due | TIMESTAMPTZ | NULLABLE |
| first_response_at | TIMESTAMPTZ | NULLABLE |
| resolved_at | TIMESTAMPTZ | NULLABLE |
| satisfaction_rating | INTEGER | NULLABLE |
| satisfaction_comment | TEXT | NULLABLE |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| closed_at | TIMESTAMPTZ | NULLABLE |

**Индексы:**
- `idx_st_ticket_number` — UNIQUE на `ticket_number`
- `idx_st_user` — на `user_id`
- `idx_st_status` — на `status`
- `idx_st_assigned` — на `assigned_to`
- `idx_st_sla` — на `sla_response_due` WHERE `first_response_at IS NULL`

### Таблица: `ticket_messages`

| Колонка | Тип | Constraints |
|---------|-----|-------------|
| id | UUID | PK |
| ticket_id | UUID | FK → support_tickets.id, NOT NULL |
| sender_id | UUID | FK → users.id, NOT NULL |
| sender_type | VARCHAR(15) | NOT NULL |
| content | TEXT | NOT NULL |
| is_internal | BOOLEAN | NOT NULL, DEFAULT FALSE |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

**Индексы:**
- `idx_tm_ticket` — на `(ticket_id, created_at)`

### Таблица: `changelog_entries`

| Колонка | Тип | Constraints |
|---------|-----|-------------|
| id | UUID | PK |
| version | VARCHAR(20) | NOT NULL |
| title | VARCHAR(200) | NOT NULL |
| content | TEXT | NOT NULL |
| type | VARCHAR(15) | NOT NULL |
| published_at | TIMESTAMPTZ | NOT NULL |
| created_by | UUID | FK → users.id, NOT NULL |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

---

## 6. Доменные события

| Событие | Поля | Описание |
|---|---|---|
| `TicketCreated` | ticket_id, ticket_number, user_id, category, priority | Тикет создан |
| `TicketAssigned` | ticket_id, assigned_to | Тикет назначен |
| `TicketStatusChanged` | ticket_id, old_status, new_status | Статус изменён |
| `TicketMessageAdded` | ticket_id, message_id, sender_type | Сообщение добавлено |
| `TicketResolved` | ticket_id | Тикет решён |
| `TicketClosed` | ticket_id | Тикет закрыт |
| `TicketReopened` | ticket_id | Тикет переоткрыт |
| `TicketSlaBreached` | ticket_id, sla_type: response \| resolution | SLA нарушен |
| `TicketSatisfactionReceived` | ticket_id, rating | Оценка получена |
| `IncidentCreated` | incident_id, title, severity | Инцидент создан |
| `IncidentUpdated` | incident_id, status | Инцидент обновлён |
| `IncidentResolved` | incident_id | Инцидент разрешён |
| `ChangelogPublished` | entry_id, version, changelog_type | Changelog опубликован |
| `ArticlePublished` | article_id, slug | Статья опубликована |
| `ArticleArchived` | article_id | Статья архивирована |

---

## 7. Exceptions

| Исключение | Описание |
|---|---|
| `TicketNotFoundException` | Тикет не найден |
| `TicketAlreadyClosedException` | Тикет уже закрыт |
| `TicketNotResolvedException` | Нельзя закрыть нерешённый тикет |
| `SupportNotAvailableException` | Поддержка недоступна на тарифе |
| `ArticleNotFoundException` | Статья не найдена |
| `IncidentNotFoundException` | Инцидент не найден |
| `DuplicateTicketNumberException` | Номер тикета уже существует |

---

## 8. Repositories

| Репозиторий | Методы |
|---|---|
| `TicketRepository` | `get_by_id`, `get_by_ticket_number`, `get_by_user`, `get_by_status`, `get_by_assigned_to`, `get_sla_breached`, `get_by_priority` |
| `HelpArticleRepository` | `get_by_id`, `get_by_slug`, `get_by_category`, `get_published`, `search` |
| `ChangelogRepository` | `get_by_id`, `get_all`, `get_by_type`, `get_latest` |
| `IncidentRepository` | `get_by_id`, `get_active`, `get_by_status` |
