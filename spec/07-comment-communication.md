# 07. Comment & Communication — Комментарии и коммуникация

## Обзор

Контекст коммуникации включает комментарии к задачам (основной канал обратной связи), встроенный мессенджер (DM и групповые чаты) и планирование совещаний. Комментарии — ядро коллаборации внутри проекта.

---

## Принципы расширяемости

1. **CommentTargetType — enum** — вместо `target_type: str`. `TASK`, `PROJECT`, `EPIC`, `MILESTONE`, `SPRINT`, `MEETING`, `DOCUMENT`. Новые сущности = значение enum.
2. **ChatType — расширяемый enum** — `DM`, `GROUP`, `CHANNEL`, `ANNOUNCEMENT`. Новые типы бесед = значение enum.
3. **MessageType — расширяемый enum** — `TEXT`, `SYSTEM`, `FILE`, `IMAGE`, `VOICE`, `VIDEO`. Новые типы сообщений = значение enum.
4. **Реакции — entity** — `Reaction` на комментариях и сообщениях. Новые emoji не требуют правки домена.
5. **Треды — entity** — под-беседа внутри чата, не путать с деревом комментариев.
6. **Совещания — рекуррентность + связь с проектом** — `RecurrenceConfig`, `MeetingType`, agenda как VO.
7. **UserPresence — вне Communication BC** — статус присутствия принадлежит Profile BC. Communication BC потребляет через events.

---

## 1. Функциональные требования

### 1.1. Комментарии к задачам

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| Текстовые комментарии (rich text) | ✅ | ✅ | ✅ | ✅ |
| @mention | ✅ | ✅ | ✅ | ✅ |
| Вложения в комментариях | ⚡ 10MB/файл | ⚡ 50MB | ⚡ 250MB | ✅ ∞ |
| Реакции (emoji) | 🔮 | 🔮 | 🔮 | 🔮 |
| Редактирование комментариев | ✅ | ✅ | ✅ | ✅ |
| Удаление комментариев | ✅ | ✅ | ✅ | ✅ |
| Закреплённые комментарии | 🔮 | 🔮 | 🔮 | 🔮 |
| Ответы (threading) | ✅ | ✅ | ✅ | ✅ |
| Системные комментарии | ✅ | ✅ | ✅ | ✅ |

**Правила:**
- Редактировать можно только свои комментарии (или Moderator+)
- Удалять: свои комментарии или Moderator+
- Системные комментарии не редактируются и не удаляются
- @mention генерирует notification для упомянутого пользователя
- Вложения привязываются к комментарию и задаче одновременно
- Threading: один уровень вложенности (ответы на ответы — flat)

### 1.2. Мессенджер

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| Личные сообщения (DM) | ❌ | ✅ | ✅ | ✅ |
| Групповые чаты | ❌ | ✅ | ✅ | ✅ |
| Отправка файлов | — | ⚡ 50MB | ⚡ 250MB | ✅ ∞ |
| Поиск по переписке | — | ✅ | ✅ | ✅ |
| Статус пользователя | — | ✅ | ✅ | ✅ |
| Макс. участников группового чата | — | 20 | 100 | ∞ |

**Статусы пользователя:**
- Online — активен
- Offline — не в сети
- Busy — занят (не беспокоить)
- Do Not Disturb — не беспокоить (без уведомлений)
- Away — отошёл (автоматически через 5 минут неактивности)

### 1.3. Совещания и созвоны

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| Планирование встреч | ❌ | ❌ | ✅ | ✅ |
| Заметки встречи | — | — | ✅ | ✅ |
| Повестка дня (agenda) | — | — | ✅ | ✅ |
| Привязка к задаче/проекту | — | — | ✅ | ✅ |

### 1.4. Роли на уровне задачи (для комментариев)

| Действие | Owner | Assignee | Guest |
|----------|-------|----------|-------|
| Добавить комментарий | ✅ | ✅ | ❌ |
| Редактировать свой комментарий | ✅ | ✅ | ❌ |
| Удалить свой комментарий | ✅ | ✅ | ❌ |
| Удалить чужой комментарий | ✅ | ❌ | ❌ |
| Просматривать комментарии | ✅ | ✅ | ✅ |

*Примечание: доступ определяется ролью проекта (см. 05-project.md), здесь упрощённо.*

---

## 2. Доменная модель

### Value Objects

| VO | Тип | Описание |
|---|---|---|
| `CommentTargetType` | Enum | `TASK`, `PROJECT`, `EPIC`, `MILESTONE`, `SPRINT`, `MEETING`, `DOCUMENT` |
| `MessageType` | Enum | `TEXT`, `SYSTEM`, `FILE`, `IMAGE`, `VOICE`, `VIDEO` |
| `ChatType` | Enum | `DM`, `GROUP`, `CHANNEL`, `ANNOUNCEMENT` |
| `MeetingStatus` | Enum | `SCHEDULED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED` |
| `MeetingType` | Enum | `IN_PERSON`, `VIDEO_CALL`, `PHONE_CALL`, `HYBRID` |
| `AttachmentType` | Enum | `IMAGE`, `VIDEO`, `FILE`, `LINK`, `VOICE` |
| `RSVPStatus` | Enum | `PENDING`, `ACCEPTED`, `DECLINED`, `TENTATIVE` |
| `ChatMemberRole` | Enum | `MEMBER`, `ADMIN`, `OWNER` |
| `RecurrencePattern` | Enum | `DAILY`, `WEEKLY`, `BIWEEKLY`, `MONTHLY` |
| `ReactionEmoji` | frozen dataclass | value: str (unicode emoji, validated) |
| `Agenda` | frozen dataclass | items: list[AgendaItem] |
| `AgendaItem` | frozen dataclass | text: str, duration_minutes: int \| None, owner_id: Id \| None |
| `RecurrenceConfig` | frozen dataclass | pattern: RecurrencePattern, interval: int, end_date: date \| None, max_occurrences: int \| None |
| `RichText` | frozen dataclass | content: str, format: RichTextFormat (`MARKDOWN` \| `WYSIWYG`) |
| `AccentColor` | frozen dataclass | hex: str (validated `#RRGGBB`) |

> **`CommentTargetType`** — enum вместо строки. Валидация существования target_id на app-слое.
>
> **`ChatType.CHANNEL`** — публичный канал workspace (аналог Slack), `ANNOUNCEMENT` — канал только для чтения.
>
> **`MeetingType`** — `HYBRID` = часть online, часть offline. Новые форматы = значение enum.
>
> **UserPresence** — вне Communication BC, принадлежит Profile BC.

### Entities

| Сущность | Поля | Описание |
|---|---|---|
| `ChatMember` | user_id: Id, role: ChatMemberRole, joined_at, last_read_at: datetime \| None | Участник чата |
| `Message` | id, chat_id, thread_id: Id \| None, sender_id, content: RichText \| None, message_type: MessageType, attachments: list[Attachment], reactions: list[Reaction], is_edited, is_deleted, reply_to_id: Id \| None | Сообщение |
| `Reaction` | user_id: Id, emoji: ReactionEmoji, created_at | Реакция на комментарий/сообщение |
| `Thread` | id, parent_message_id: Id, title: str \| None, is_resolved: bool | Тред внутри чата |
| `MeetingParticipant` | user_id: Id, is_mandatory: bool, joined_at \| None, rsvp_status: RSVPStatus | Участник совещания |
| `MeetingNote` | id, content: RichText \| None, author_id, created_at | Заметка совещания |
| `MeetingActionItem` | id, text, assignee_id: Id \| None, due_date: date \| None, is_completed | Action item совещания |
| `Attachment` | id, file_id: Id (opaque, из FileStorage BC), attachment_type: AttachmentType, name, size_bytes, preview_url: Url \| None | Вложение |

> **`Message`** — `thread_id` для тредов, `reactions`, `reply_to_id` для ответа на сообщение. `is_deleted` — soft delete.
>
> **`Reaction`** — уникальность по (user_id, emoji). Один пользователь может поставить несколько разных emoji.
>
> **`Thread`** — под-беседа от конкретного сообщения. `is_resolved` — тред закрыт.
>
> **`MeetingActionItem`** — связь с Task BC через opaque `task_id` на app-слое.

### Aggregates

#### Comment (Aggregate Root)

Поля:
- author_id: Id
- target_type: CommentTargetType
- target_id: Id (opaque, из соответствующего BC)
- content: RichText | None
- parent_comment_id: Id | None (для ответов, древовидная структура)
- attachments: list[Attachment]
- reactions: list[Reaction]
- is_pinned: bool
- is_system: bool
- is_deleted: bool
- created_at: datetime
- updated_at: datetime

Методы:
- `create(author_id, target_type, target_id, content)` → `Comment` (factory)
- `create_system(target_type, target_id, content)` → системный (factory, is_system=True)
- `update(content)` — только не-системные, не-удалённые
- `delete()` — soft delete (is_deleted=True), только не-системные
- `pin()` / `unpin()`
- `add_reaction(user_id, emoji)` / `remove_reaction(user_id, emoji)`
- `add_attachment(attachment)` / `remove_attachment(attachment_id)`

Инварианты:
- Системный комментарий нельзя редактировать/удалять
- Удалённый нельзя редактировать
- Реакции уникальны по (user_id, emoji)
- `target_type` + `target_id` — валидация на app-слое

#### Chat (Aggregate Root)

Поля:
- chat_type: ChatType
- name: str | None (обязательно для GROUP/CHANNEL/ANNOUNCEMENT)
- description: str | None
- icon_url: Url | None
- color: AccentColor | None
- workspace_id: Id | None (для CHANNEL/ANNOUNCEMENT)
- members: list[ChatMember]
- threads: list[Thread]
- last_message_at: datetime | None
- is_archived: bool
- created_at: datetime
- updated_at: datetime

Методы:
- `create_dm(user_a, user_b)` / `create_group(name, creator_id)` / `create_channel(name, ws_id, creator_id)` / `create_announcement(name, ws_id, creator_id)`
- `update_info(name=None, description=None, icon_url=None, color=None)`
- `add_member(user_id)` / `remove_member(user_id)` — только GROUP/CHANNEL
- `change_member_role(user_id, new_role)` — OWNER/ADMIN
- `mark_as_read(user_id, read_at)`
- `create_thread(parent_message_id, title)` / `resolve_thread(thread_id)` / `reopen_thread(thread_id)`
- `archive()` / `restore()`

Инварианты:
- DM: строго 2 участника, нельзя добавить/удалить, все = MEMBER
- GROUP: минимум 1 OWNER
- CHANNEL: привязан к workspace_id
- ANNOUNCEMENT: только OWNER/ADMIN отправляют сообщения
- DM между двумя пользователями уникален
- Архивированный чат не принимает сообщения

#### Meeting (Aggregate Root)

Поля:
- title: str
- description: RichText | None
- meeting_type: MeetingType
- agenda: Agenda | None
- status: MeetingStatus
- scheduled_at: datetime
- duration_minutes: int | None
- location: str | None (IN_PERSON)
- conference_url: Url | None (VIDEO_CALL/HYBRID)
- project_id: Id | None (opaque, из Project BC)
- workspace_id: Id (opaque)
- organizer_id: Id
- participants: list[MeetingParticipant]
- notes: list[MeetingNote]
- action_items: list[MeetingActionItem]
- recurrence: RecurrenceConfig | None
- created_at: datetime
- updated_at: datetime

Методы:
- `create(title, scheduled_at, workspace_id, organizer_id, meeting_type, ...)` → `Meeting`
- `update(title, agenda, scheduled_at, duration_minutes, description, location, conference_url)`
- `add_participant(user_id, is_mandatory)` / `remove_participant(user_id)`
- `update_rsvp(user_id, rsvp_status)`
- `start()` / `complete()` / `cancel()`
- `add_note(content, author_id)` — только IN_PROGRESS/COMPLETED
- `add_action_item(text, assignee_id, due_date)` / `complete_action_item(id)` / `remove_action_item(id)`

Инварианты:
- Заметки — только к начатому/завершённому совещанию
- Завершённое нельзя начать заново
- Отменённое нельзя начать
- Organizer автоматически participant с is_mandatory=True
- RSVP: PENDING → ACCEPTED/DECLINED/TENTATIVE, TENTATIVE → ACCEPTED/DECLINED

---

## 3. Бизнес-правила

### Комментарии
1. Автор может редактировать/удалять свой комментарий
2. Moderator+ может удалять любые комментарии
3. Системные комментарии (is_system=true) неизменяемы
4. Threading: один уровень (ответ на комментарий, но не ответ на ответ — parent всегда root)
5. @mention: извлекаются из content, валидируются против участников проекта
6. Soft-delete: удалённые комментарии помечаются, но данные хранятся
7. Вложения: максимум 10 файлов на комментарий

### Мессенджер
8. DM: между двумя участниками workspace; conversation создаётся при первом сообщении
9. Group chat: создатель — admin; может добавлять/удалять участников
10. Участники: только члены workspace
11. Soft-delete сообщений: текст заменяется на "Сообщение удалено"
12. Максимум 100 сообщений без подтверждения аккаунта

### Совещания
13. Организатор может редактировать/отменять встречу
14. Участники получают notification при создании/изменении/отмене
15. Notes доступны всем attendees после завершения

---

## 4. API Endpoints

### 4.1. Комментарии

```
GET /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/{task_id}/comments
```

**Query params:** `page`, `limit`, `sort` (asc/desc by created_at)

---

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/{task_id}/comments
```

**Request:**
```json
{
  "content": "Looks good! @john please review the auth flow.",
  "parent_comment_id": null,
  "attachment_ids": ["file_uuid1"]
}
```

---

```
PATCH /api/v1/.../comments/{comment_id}
```

**Request:**
```json
{
  "content": "Updated content"
}
```

---

```
DELETE /api/v1/.../comments/{comment_id}
```

---

```
POST /api/v1/.../comments/{comment_id}/pin
```

---

```
DELETE /api/v1/.../comments/{comment_id}/pin
```

### 4.2. Мессенджер

```
GET /api/v1/workspaces/{ws_id}/conversations
```

**Query params:** `type` (dm/group), `page`, `limit`

---

```
POST /api/v1/workspaces/{ws_id}/conversations
```

**Request (DM):**
```json
{
  "type": "dm",
  "participant_id": "user_uuid"
}
```

**Request (Group):**
```json
{
  "type": "group",
  "name": "Backend Team Chat",
  "participant_ids": ["uuid1", "uuid2", "uuid3"]
}
```

---

```
GET /api/v1/workspaces/{ws_id}/conversations/{conv_id}/messages
```

**Query params:** `before_id`, `after_id`, `limit` (cursor-based pagination)

---

```
POST /api/v1/workspaces/{ws_id}/conversations/{conv_id}/messages
```

**Request:**
```json
{
  "content": "Hello team!",
  "attachment_ids": []
}
```

---

```
PATCH /api/v1/workspaces/{ws_id}/conversations/{conv_id}/messages/{msg_id}
```

---

```
DELETE /api/v1/workspaces/{ws_id}/conversations/{conv_id}/messages/{msg_id}
```

---

```
POST /api/v1/workspaces/{ws_id}/conversations/{conv_id}/read
```

**Request:**
```json
{
  "last_read_message_id": "msg_uuid"
}
```

---

```
POST /api/v1/workspaces/{ws_id}/conversations/{conv_id}/participants
```

---

```
DELETE /api/v1/workspaces/{ws_id}/conversations/{conv_id}/participants/{user_id}
```

### 4.3. Presence

```
PUT /api/v1/workspaces/{ws_id}/presence
```

**Request:**
```json
{
  "status": "busy",
  "custom_status": "In a meeting"
}
```

---

```
GET /api/v1/workspaces/{ws_id}/presence
```

*Список presence всех участников workspace (для sidebar)*

### 4.4. Совещания

```
POST /api/v1/workspaces/{ws_id}/meetings
```

**Request:**
```json
{
  "title": "Sprint Review",
  "start_time": "2025-02-14T15:00:00Z",
  "end_time": "2025-02-14T16:00:00Z",
  "agenda": "## Review\n- Feature A\n- Feature B",
  "attendee_ids": ["uuid1", "uuid2"],
  "project_id": "project_uuid",
  "location": "https://meet.google.com/abc"
}
```

---

```
GET /api/v1/workspaces/{ws_id}/meetings
```

**Query params:** `from`, `to`, `status`, `project_id`

---

```
PATCH /api/v1/workspaces/{ws_id}/meetings/{meeting_id}
```

---

```
DELETE /api/v1/workspaces/{ws_id}/meetings/{meeting_id}
```

---

```
PUT /api/v1/workspaces/{ws_id}/meetings/{meeting_id}/respond
```

**Request:**
```json
{
  "response": "accepted"
}
```

---

```
PUT /api/v1/workspaces/{ws_id}/meetings/{meeting_id}/notes
```

**Request:**
```json
{
  "notes": "## Decisions\n- Approved feature A\n- Delayed feature B"
}
```

---

## 5. Схема БД

### Таблица: `comments`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| task_id | UUID | FK → tasks.id, NOT NULL | |
| author_id | UUID | FK → users.id, NOT NULL | |
| parent_comment_id | UUID | FK → comments.id, NULLABLE | Threading |
| content | TEXT | NOT NULL | Rich text |
| is_system | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| is_pinned | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| is_edited | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| mentions | JSONB | NOT NULL, DEFAULT '[]' | User IDs |
| edited_at | TIMESTAMPTZ | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**Индексы:**
- `idx_comment_task` — на `task_id`
- `idx_comment_author` — на `author_id`
- `idx_comment_parent` — на `parent_comment_id`
- `idx_comment_task_created` — на `(task_id, created_at)`

### Таблица: `comment_attachments`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| comment_id | UUID | FK → comments.id, NOT NULL | |
| file_id | UUID | FK → files.id, NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

### Таблица: `comment_reactions` (🔮 future)

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| comment_id | UUID | FK → comments.id, NOT NULL | |
| user_id | UUID | FK → users.id, NOT NULL | |
| emoji | VARCHAR(10) | NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_cr_comment_user` — UNIQUE на `(comment_id, user_id, emoji)`

### Таблица: `conversations`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| workspace_id | UUID | FK → workspaces.id, NOT NULL | |
| type | VARCHAR(10) | NOT NULL | dm/group |
| name | VARCHAR(100) | NULLABLE | Для groups |
| created_by | UUID | FK → users.id, NOT NULL | |
| last_message_at | TIMESTAMPTZ | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_conv_ws` — на `workspace_id`
- `idx_conv_last_msg` — на `(workspace_id, last_message_at DESC)`

### Таблица: `conversation_participants`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| conversation_id | UUID | FK → conversations.id, NOT NULL | |
| user_id | UUID | FK → users.id, NOT NULL | |
| role | VARCHAR(10) | NOT NULL, DEFAULT 'member' | |
| last_read_message_id | UUID | NULLABLE | |
| muted | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| joined_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| left_at | TIMESTAMPTZ | NULLABLE | |

**Индексы:**
- `idx_cp_conv_user` — UNIQUE на `(conversation_id, user_id)`
- `idx_cp_user` — на `user_id`

### Таблица: `messages`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| conversation_id | UUID | FK → conversations.id, NOT NULL | |
| sender_id | UUID | FK → users.id, NOT NULL | |
| content | TEXT | NOT NULL | |
| is_edited | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| edited_at | TIMESTAMPTZ | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**Индексы:**
- `idx_msg_conv` — на `conversation_id`
- `idx_msg_conv_created` — на `(conversation_id, created_at DESC)`

### Таблица: `message_attachments`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| message_id | UUID | FK → messages.id, NOT NULL | |
| file_id | UUID | FK → files.id, NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

### Таблица: `meetings`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| workspace_id | UUID | FK → workspaces.id, NOT NULL | |
| title | VARCHAR(200) | NOT NULL | |
| description | TEXT | NULLABLE | |
| agenda | TEXT | NULLABLE | Rich text |
| notes | TEXT | NULLABLE | Rich text |
| start_time | TIMESTAMPTZ | NOT NULL | |
| end_time | TIMESTAMPTZ | NOT NULL | |
| location | VARCHAR(500) | NULLABLE | |
| organizer_id | UUID | FK → users.id, NOT NULL | |
| project_id | UUID | FK → projects.id, NULLABLE | |
| task_id | UUID | FK → tasks.id, NULLABLE | |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'scheduled' | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_meeting_ws` — на `workspace_id`
- `idx_meeting_time` — на `(workspace_id, start_time)`
- `idx_meeting_project` — на `project_id`

### Таблица: `meeting_attendees`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| meeting_id | UUID | FK → meetings.id, NOT NULL | |
| user_id | UUID | FK → users.id, NOT NULL | |
| response | VARCHAR(15) | NOT NULL, DEFAULT 'pending' | |
| responded_at | TIMESTAMPTZ | NULLABLE | |

**Индексы:**
- `idx_ma_meeting_user` — UNIQUE на `(meeting_id, user_id)`

### Таблица: `user_presences`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| user_id | UUID | NOT NULL | |
| workspace_id | UUID | NOT NULL | |
| status | VARCHAR(10) | NOT NULL, DEFAULT 'offline' | |
| custom_status | VARCHAR(100) | NULLABLE | |
| last_seen_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_up_pk` — PRIMARY KEY на `(user_id, workspace_id)`

---

## 6. Доменные события

| Событие | Поля | Описание |
|---|---|---|
| `CommentAdded` | comment_id, target_type, target_id, author_id | Комментарий добавлен |
| `CommentUpdated` | comment_id | Комментарий обновлён |
| `CommentDeleted` | comment_id | Комментарий удалён (soft) |
| `CommentReplied` | comment_id, parent_comment_id | Ответ на комментарий |
| `CommentReactionAdded` | comment_id, user_id, emoji | Реакция на комментарий |
| `CommentReactionRemoved` | comment_id, user_id, emoji | Реакция снята |
| `MessageSent` | message_id, chat_id, sender_id, message_type | Сообщение отправлено |
| `MessageUpdated` | message_id | Сообщение обновлено |
| `MessageDeleted` | message_id | Сообщение удалено (soft) |
| `MessageReactionAdded` | message_id, user_id, emoji | Реакция на сообщение |
| `MessageReactionRemoved` | message_id, user_id, emoji | Реакция снята |
| `ChatCreated` | chat_id, chat_type | Чат создан |
| `ChatUpdated` | chat_id, changed_fields: list[str] | Чат обновлён |
| `ChatMemberAdded` | chat_id, user_id | Участник добавлен |
| `ChatMemberRemoved` | chat_id, user_id | Участник удалён |
| `ChatMemberRoleChanged` | chat_id, user_id, new_role | Роль изменена |
| `ThreadCreated` | thread_id, chat_id, parent_message_id | Тред создан |
| `ThreadResolved` | thread_id | Тред закрыт |
| `ThreadReopened` | thread_id | Тред открыт заново |
| `MeetingScheduled` | meeting_id, title, scheduled_at, meeting_type | Совещание запланировано |
| `MeetingUpdated` | meeting_id, changed_fields: list[str] | Совещание обновлено |
| `MeetingCancelled` | meeting_id | Совещание отменено |
| `MeetingStarted` | meeting_id | Совещание начато |
| `MeetingCompleted` | meeting_id | Совещание завершено |
| `MeetingNoteAdded` | meeting_id, note_id | Заметка добавлена |
| `MeetingActionItemAdded` | meeting_id, action_item_id | Action item добавлен |
| `MeetingActionItemCompleted` | meeting_id, action_item_id | Action item завершён |
| `MeetingRSVPUpdated` | meeting_id, user_id, rsvp_status | RSVP обновлён |
| `RecurringMeetingCreated` | source_meeting_id, new_meeting_id | Повторяющееся совещание |
| `UserMentioned` | mentioned_user_id, source_type, source_id | Пользователь упомянут |

---

## 7. Exceptions

| Исключение | Описание |
|---|---|
| `CommentNotFoundException` | Комментарий не найден |
| `CommentDeletedException` | Комментарий удалён |
| `CannotDeleteCommentException` | Нельзя удалить (системный) |
| `CannotUpdateCommentException` | Нельзя редактировать (системный/удалённый) |
| `DuplicateReactionException` | Реакция уже поставлена |
| `ChatNotFoundException` | Чат не найден |
| `NotChatMemberException` | Не участник чата |
| `ChatAlreadyExistsException` | DM уже существует |
| `CannotAddMemberToDMException` | Нельзя добавить в DM |
| `CannotRemoveFromDMException` | Нельзя удалить из DM |
| `InvalidChatMemberRoleException` | Некорректная роль |
| `ThreadNotFoundException` | Тред не найден |
| `ThreadAlreadyResolvedException` | Тред уже закрыт |
| `MeetingNotFoundException` | Совещание не найдено |
| `CannotAddMeetingNoteException` | Заметку можно добавить только к начатому/завершённому |
| `MeetingAlreadyStartedException` | Уже начато |
| `MeetingAlreadyCompletedException` | Уже завершено |
| `InvalidRSVPStatusTransitionException` | Некорректный переход RSVP |
| `MeetingActionItemNotFoundException` | Action item не найден |
| `RecurringMeetingConfigurationException` | Некорректная конфигурация повторения |

---

## 8. Repositories

| Репозиторий | Методы |
|---|---|
| `CommentRepository` | `get_by_id`, `get_by_target`, `get_by_target_and_type`, `get_replies`, `get_by_author`, `search`, `count_by_target` |
| `ChatRepository` | `get_by_id`, `get_by_member`, `get_dm_between`, `get_by_workspace`, `get_by_type`, `search` |
| `MessageRepository` | `get_by_id`, `get_by_chat`, `get_by_thread`, `get_by_chat_after`, `search`, `count_unread` |
| `MeetingRepository` | `get_by_id`, `get_by_workspace`, `get_by_project`, `get_upcoming_by_participant`, `get_by_organizer`, `get_by_status`, `search` |
