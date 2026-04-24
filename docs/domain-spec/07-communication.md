# Communication BC — Спецификация

> Путь: `app/context/communication/domain`
> Исходные требования: §7 (Комментарии и коммуникация)

## Контекст

Communication BC отвечает за комментарии к любым сущностям, мессенджер (DM/групповые чаты/каналы), совещания, упоминания и реакции. Комментарии привязываются к `CommentTargetType` + `target_id` (opaque), что позволяет комментировать любые сущности из любых BC. Чаты поддерживают треды. Совещания поддерживают рекуррентность и связь с проектами.

---

## Принципы расширяемости

1. **CommentTargetType — enum** — вместо магической строки `target_type: str`. Новые комментируемые сущности = значение enum.
2. **ChatType — расширяемый enum** — `CHANNEL`, `ANNOUNCEMENT` помимо DM/GROUP. Новые типы бесед = значение enum.
3. **MessageType — расширяемый enum** — `FILE`, `IMAGE`, `VOICE`, `VIDEO` помимо TEXT/SYSTEM. Новые типы сообщений = значение enum.
4. **Реакции — entity** — `Reaction` на комментариях и сообщениях. Новые emoji не требуют правки домена.
5. **Треды — entity** — под-беседа внутри чата, не путать с деревом комментариев. Расширяемая модель.
6. **Совещания — рекуррентность + связь с проектом** — `RecurrenceConfig`, `project_id` (opaque). Новые форматы совещаний = расширение MeetingType.
7. **UserPresence — вне Communication BC** — статус присутствия принадлежит Profile BC. Communication BC только потребляет его через events.

---

## Value Objects

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `CommentTargetType` | Enum | `TASK`, `PROJECT`, `EPIC`, `MILESTONE`, `SPRINT`, `MEETING`, `DOCUMENT` | §7.1 |
| `MessageType` | Enum | `TEXT`, `SYSTEM`, `FILE`, `IMAGE`, `VOICE`, `VIDEO` | §7.1 |
| `ChatType` | Enum | `DM`, `GROUP`, `CHANNEL`, `ANNOUNCEMENT` | §7.2 |
| `MeetingStatus` | Enum | `SCHEDULED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED` | §7.3 |
| `MeetingType` | Enum | `IN_PERSON`, `VIDEO_CALL`, `PHONE_CALL`, `HYBRID` | §7.3 |
| `AttachmentType` | Enum | `IMAGE`, `VIDEO`, `FILE`, `LINK`, `VOICE` | §7.1 |
| `Agenda` | frozen dataclass | items: list[AgendaItem] | §7.3 |
| `AgendaItem` | frozen dataclass | text: str, duration_minutes: int \| None, owner_id: Id \| None | §7.3 |
| `ReactionEmoji` | frozen dataclass | value: str (unicode emoji, validated) | §7.1 |
| `RecurrencePattern` | Enum | `DAILY`, `WEEKLY`, `BIWEEKLY`, `MONTHLY` | §7.3 |
| `RecurrenceConfig` | frozen dataclass | pattern: RecurrencePattern, interval: int, end_date: date \| None, max_occurrences: int \| None | §7.3 |
| `AccentColor` | frozen dataclass | hex: str (validated #RRGGBB) | §7.2 |
| `RichText` | frozen dataclass | content: str, format: RichTextFormat | §7.1 |
| `RichTextFormat` | Enum | `MARKDOWN`, `WYSIWYG` | §7.1 |

> **`CommentTargetType`** — enum вместо `target_type: str`. Новые комментируемые сущности (например, `DOCUMENT`, `AUTOMATION_RULE`) = значение enum. Валидация на app-слое: проверка существования target_id в соответствующем BC.
>
> **`MessageType`** — `FILE` — файловое вложение с превью, `IMAGE` — изображение с thumbnail, `VOICE` — голосовое сообщение, `VIDEO` — видео. Новые типы (например, `POLL`, `CARD`) = значение enum.
>
> **`ChatType`** — `CHANNEL` — публичный канал в workspace (аналог Slack channel), `ANNOUNCEMENT` — канал только для чтения с авторами. Новые типы (например, `SUPPORT`, `AI_CHAT`) = значение enum.
>
> **`MeetingType`** — определяет формат совещания. `HYBRID` — часть участников очно, часть онлайн. Новые форматы = значение enum.
>
> **`AgendaItem`** — типизированная замена `items: list[str]`. Каждый пункт имеет текст, опциональную длительность и ответственного. Расширяемо.
>
> **`ReactionEmoji`** — валидированный unicode emoji. Список разрешённых emoji настраивается на app-слое. Новые реакции не требуют правки домена.
>
> **`UserPresence`** — убран из Communication BC. Статус присутствия (ONLINE/OFFLINE/BUSY/DND) принадлежит Profile BC. Communication BC потребляет его через events для отображения в UI.

## Entities

| Сущность | Поля | Описание | Исходное требование |
|---|---|---|---|
| `ChatMember` | user_id: Id, role: ChatMemberRole, joined_at: datetime, last_read_at: datetime \| None | Участник чата | §7.2 |
| `ChatMemberRole` | Enum | `MEMBER`, `ADMIN`, `OWNER` | §7.2 |
| `Message` | id: Id, chat_id: Id, thread_id: Id \| None, sender_id: Id, content: RichText \| None, message_type: MessageType, attachments: list[Attachment], reactions: list[Reaction], is_edited: bool, is_deleted: bool, reply_to_id: Id \| None, created_at: datetime, updated_at: datetime | Сообщение в чате | §7.2 |
| `Reaction` | user_id: Id, emoji: ReactionEmoji, created_at: datetime | Реакция на комментарий/сообщение | §7.1 |
| `Thread` | id: Id, parent_message_id: Id, title: str \| None, is_resolved: bool, created_at: datetime | Тред внутри чата | §7.2 |
| `MeetingParticipant` | user_id: Id, is_mandatory: bool, joined_at: datetime \| None, rsvp_status: RSVPStatus | Участник совещания | §7.3 |
| `RSVPStatus` | Enum | `PENDING`, `ACCEPTED`, `DECLINED`, `TENTATIVE` | §7.3 |
| `MeetingNote` | id: Id, content: RichText \| None, author_id: Id, created_at: datetime | Заметка совещания | §7.3 |
| `MeetingActionItem` | id: Id, text: str, assignee_id: Id \| None, due_date: date \| None, is_completed: bool | Action item совещания | §7.3 |
| `Attachment` | id: Id, file_id: Id (opaque, из FileStorage BC), url: Url \| None, attachment_type: AttachmentType, name: str, size_bytes: int, preview_url: Url \| None, created_at: datetime | Вложение в комментарии/сообщении | §7.1 |

> **`ChatMember`** — добавлены `role` (для управления каналами), `last_read_at` (для unread count). Unread count вычисляется на app-слое: количество сообщений после `last_read_at`.
>
> **`ChatMemberRole`** — `OWNER` — создатель чата/канала, `ADMIN` — может управлять участниками, `MEMBER` — обычный участник. Для DM все участники = `MEMBER`.
>
> **`Message`** — добавлены `thread_id` (для тредов), `reactions`, `attachments` (встроенные), `reply_to_id` (ответ на конкретное сообщение). `is_deleted` — soft delete, содержимое заменяется на "Сообщение удалено".
>
> **`Reaction`** — одна реакция = один пользователь + один emoji. Уникальность по (user_id, emoji). Один пользователь может поставить несколько разных emoji на один комментарий/сообщение.
>
> **`Thread`** — под-беседа внутри чата, инициированная от конкретного сообщения (`parent_message_id`). `is_resolved` — тред можно закрыть/разрешить. Не путать с деревом комментариев (Comment + `parent_comment_id`).
>
> **`MeetingParticipant.rsvp_status`** — ответ на приглашение. `PENDING` — не ответил, `ACCEPTED` — примет, `DECLINED` — отклонил, `TENTATIVE` — под вопросом.
>
> **`MeetingActionItem`** — задачи/действия, возникшие на совещании. Связь с Task BC — опциональная, через opaque `task_id` на app-слое.
>
> **`Attachment.preview_url`** — URL превью для изображений/видео. Генерируется FileStorage BC.

## Domain Events

| Событие | Поля | Описание | Исходное требование |
|---|---|---|---|
| `CommentAdded` | comment_id, target_type: CommentTargetType, target_id, author_id | Комментарий добавлен | §7.1 |
| `CommentUpdated` | comment_id | Комментарий обновлён | §7.1 |
| `CommentDeleted` | comment_id | Комментарий удалён (soft) | §7.1 |
| `CommentReplied` | comment_id, parent_comment_id | Ответ на комментарий | §7.1 |
| `CommentReactionAdded` | comment_id, user_id, emoji | Реакция на комментарий | §7.1 |
| `CommentReactionRemoved` | comment_id, user_id, emoji | Реакция снята | §7.1 |
| `MessageSent` | message_id, chat_id, sender_id, message_type | Сообщение отправлено | §7.2 |
| `MessageUpdated` | message_id | Сообщение обновлено | §7.2 |
| `MessageDeleted` | message_id | Сообщение удалено (soft) | §7.2 |
| `MessageReactionAdded` | message_id, user_id, emoji | Реакция на сообщение | §7.2 |
| `MessageReactionRemoved` | message_id, user_id, emoji | Реакция снята | §7.2 |
| `ChatCreated` | chat_id, chat_type: ChatType | Чат создан | §7.2 |
| `ChatUpdated` | chat_id, changed_fields: list[str] | Чат обновлён | §7.2 |
| `ChatMemberAdded` | chat_id, user_id | Участник добавлен | §7.2 |
| `ChatMemberRemoved` | chat_id, user_id | Участник удалён | §7.2 |
| `ChatMemberRoleChanged` | chat_id, user_id, new_role | Роль участника изменена | §7.2 |
| `ThreadCreated` | thread_id, chat_id, parent_message_id | Тред создан | §7.2 |
| `ThreadResolved` | thread_id | Тред закрыт | §7.2 |
| `ThreadReopened` | thread_id | Тред открыт заново | §7.2 |
| `MeetingScheduled` | meeting_id, title, scheduled_at, meeting_type | Совещание запланировано | §7.3 |
| `MeetingUpdated` | meeting_id, changed_fields: list[str] | Совещание обновлено | §7.3 |
| `MeetingCancelled` | meeting_id | Совещание отменено | §7.3 |
| `MeetingStarted` | meeting_id | Совещание начато | §7.3 |
| `MeetingCompleted` | meeting_id | Совещание завершено | §7.3 |
| `MeetingNoteAdded` | meeting_id, note_id | Заметка добавлена | §7.3 |
| `MeetingActionItemAdded` | meeting_id, action_item_id | Action item добавлен | §7.3 |
| `MeetingActionItemCompleted` | meeting_id, action_item_id | Action item завершён | §7.3 |
| `MeetingRSVPUpdated` | meeting_id, user_id, rsvp_status | RSVP ответ обновлён | §7.3 |
| `RecurringMeetingCreated` | source_meeting_id, new_meeting_id | Повторяющееся совещание создано | §7.3 |
| `UserMentioned` | mentioned_user_id, source_type: CommentTargetType, source_id | Пользователь упомянут | §7.1 |

> **`CommentAdded.target_type`** — `CommentTargetType` enum вместо строки. Позволяет типобезопасно маршрутизировать события.
>
> **`CommentReactionAdded`/`MessageReactionAdded`** — отдельные events для реакций. Позволяют уведомлять автора комментария/сообщения о реакции.
>
> **`ThreadCreated`/`ThreadResolved`** — треды имеют свой жизненный цикл. `ThreadResolved` — тред закрыт (решён), `ThreadReopened` — открыт заново.
>
> **`MeetingActionItemAdded`** — при добавлении action item на совещании. App-layer handler может создать задачу в Task BC.
>
> **`MeetingRSVPUpdated`** — участник ответил на приглашение. Позволяет организатору видеть кто придёт.
>
> **`RecurringMeetingCreated`** — app-layer handler создаёт следующее совещание из `RecurrenceConfig`.

## Exceptions

| Исключение | Описание |
|---|---|
| `CommentNotFoundException` | Комментарий не найден |
| `CommentDeletedException` | Комментарий удалён |
| `CannotDeleteCommentException` | Нельзя удалить комментарий (системный) |
| `CannotUpdateCommentException` | Нельзя редактировать комментарий (системный/удалённый) |
| `DuplicateReactionException` | Реакция уже поставлена |
| `ChatNotFoundException` | Чат не найден |
| `NotChatMemberException` | Не участник чата |
| `ChatAlreadyExistsException` | DM между пользователями уже существует |
| `CannotAddMemberToDMException` | Нельзя добавить участника в DM |
| `CannotRemoveFromDMException` | Нельзя удалить участника из DM |
| `InvalidChatMemberRoleException` | Некорректная роль участника |
| `ThreadNotFoundException` | Тред не найден |
| `ThreadAlreadyResolvedException` | Тред уже закрыт |
| `MeetingNotFoundException` | Совещание не найдено |
| `CannotAddMeetingNoteException` | Заметку можно добавить только к начатому/завершённому совещанию |
| `MeetingAlreadyStartedException` | Совещание уже начато |
| `MeetingAlreadyCompletedException` | Совещание уже завершено |
| `InvalidRSVPStatusTransitionException` | Некорректный переход RSVP статуса |
| `MeetingActionItemNotFoundException` | Action item не найден |
| `RecurringMeetingConfigurationException` | Некорректная конфигурация повторения |

## Aggregates

### Comment (Aggregate Root)

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
- `create_system(target_type, target_id, content)` → системный комментарий (factory, is_system=True)
- `update(content)` — только для не-системных и не-удалённых
- `delete()` — soft delete (is_deleted=True), только для не-системных
- `pin()` / `unpin()`
- `add_reaction(user_id, emoji: ReactionEmoji)`
- `remove_reaction(user_id, emoji: ReactionEmoji)`
- `add_attachment(attachment: Attachment)`
- `remove_attachment(attachment_id)`

Инварианты:
- Системный комментарий нельзя редактировать/удалять
- Удалённый комментарий нельзя редактировать
- Ответы формируют древовидную структуру (проверка циклов на app-слое)
- Реакции уникальны по (user_id, emoji) — один пользователь один emoji один раз
- `target_type` + `target_id` — валидация существования target на app-слое

### Chat (Aggregate Root)

Поля:
- chat_type: ChatType
- name: str | None (обязательно для GROUP/CHANNEL/ANNOUNCEMENT)
- description: str | None
- icon_url: Url | None
- color: AccentColor | None
- workspace_id: Id | None (opaque, для CHANNEL/ANNOUNCEMENT)
- members: list[ChatMember]
- threads: list[Thread]
- last_message_at: datetime | None
- is_archived: bool
- created_at: datetime
- updated_at: datetime

Методы:
- `create_dm(user_a, user_b)` → `Chat` (factory, chat_type=DM)
- `create_group(name, creator_id)` → `Chat` (factory, chat_type=GROUP)
- `create_channel(name, workspace_id, creator_id)` → `Chat` (factory, chat_type=CHANNEL)
- `create_announcement(name, workspace_id, creator_id)` → `Chat` (factory, chat_type=ANNOUNCEMENT)
- `update_info(name=None, description=None, icon_url=None, color=None)`
- `add_member(user_id)` — только для GROUP/CHANNEL
- `remove_member(user_id)` — только для GROUP/CHANNEL
- `change_member_role(user_id, new_role: ChatMemberRole)` — только OWNER/ADMIN могут
- `is_member(user_id)` → bool
- `mark_as_read(user_id, read_at: datetime)` — обновляет ChatMember.last_read_at
- `create_thread(parent_message_id, title=None)` → `Thread`
- `resolve_thread(thread_id)`
- `reopen_thread(thread_id)`
- `archive()` / `restore()`

Инварианты:
- DM: строго 2 участника, нельзя добавить/удалить, все = MEMBER
- GROUP: можно добавлять/удалять участников, минимум 1 OWNER
- CHANNEL: привязан к workspace_id, публичный — любой член workspace может присоединиться
- ANNOUNCEMENT: только OWNER/ADMIN могут отправлять сообщения, все могут читать
- DM между двумя пользователями — уникальный (проверка на repository)
- Архивированный чат не принимает сообщения
- Тред привязан к конкретному сообщению (parent_message_id)

### Meeting (Aggregate Root)

Поля:
- title: str
- description: RichText | None
- meeting_type: MeetingType
- agenda: Agenda | None
- status: MeetingStatus
- scheduled_at: datetime
- duration_minutes: int | None
- location: str | None (для IN_PERSON)
- conference_url: Url | None (для VIDEO_CALL/HYBRID)
- project_id: Id | None (opaque, из Project BC — связь с проектом)
- workspace_id: Id (opaque, из Workspace BC)
- organizer_id: Id
- participants: list[MeetingParticipant]
- notes: list[MeetingNote]
- action_items: list[MeetingActionItem]
- recurrence: RecurrenceConfig | None
- created_at: datetime
- updated_at: datetime

Методы:
- `create(title, scheduled_at, workspace_id, organizer_id, meeting_type, agenda=None, duration_minutes=None, project_id=None, recurrence=None)` → `Meeting` (factory)
- `update(title=None, agenda=None, scheduled_at=None, duration_minutes=None, description=None, location=None, conference_url=None)`
- `add_participant(user_id, is_mandatory=True)`
- `remove_participant(user_id)`
- `update_rsvp(user_id, rsvp_status: RSVPStatus)`
- `start()`
- `complete()`
- `cancel()`
- `add_note(content, author_id)` — только если IN_PROGRESS или COMPLETED
- `add_action_item(text, assignee_id=None, due_date=None)`
- `complete_action_item(action_item_id)`
- `remove_action_item(action_item_id)`

Инварианты:
- Заметки можно добавлять только к начатому/завершённому совещанию
- Завершённое совещание нельзя начать заново
- Отменённое совещание нельзя начать
- `MeetingType.IN_PERSON` → `location` должен быть заполнен (проверка на app-слое)
- `MeetingType.VIDEO_CALL` / `HYBRID` → `conference_url` должен быть заполнен (проверка на app-слое)
- Organizer автоматически добавляется как participant с `is_mandatory=True`
- Задача с `recurrence` при завершении может автоматически создавать следующее совещание (app-layer handler)
- RSVP переходы: PENDING → ACCEPTED/DECLINED/TENTATIVE, TENTATIVE → ACCEPTED/DECLINED, DECLINED → TENTATIVE

## Repositories

| Репозиторий | Методы |
|---|---|
| `CommentRepository` | `get_by_id`, `get_by_target`, `get_by_target_and_type`, `get_replies`, `get_by_author`, `search`, `count_by_target` |
| `ChatRepository` | `get_by_id`, `get_by_member`, `get_dm_between`, `get_by_workspace`, `get_by_type`, `search` |
| `MessageRepository` | `get_by_id`, `get_by_chat`, `get_by_thread`, `get_by_chat_after`, `search`, `count_unread` |
| `MeetingRepository` | `get_by_id`, `get_by_workspace`, `get_by_project`, `get_upcoming_by_participant`, `get_by_organizer`, `get_by_status`, `search` |

> **`MessageRepository`** — выделен из ChatRepository. Сообщения — отдельная сущность с пагинацией. `get_by_chat_after` — для загрузки сообщений после определённого времени (real-time). `count_unread` — количество непрочитанных сообщений после `ChatMember.last_read_at`.
>
> **`CommentRepository.get_by_target_and_type`** — фильтрация по `CommentTargetType`. Например, все комментарии к задачам проекта.
>
> **`MeetingRepository.get_by_project`** — совещания привязаны к проекту через `project_id`.
