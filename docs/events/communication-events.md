# События Communication BC

## События, которые отдаёт Communication BC

### Chat Events

| Событие | Описание | Поля |
|---|---|---|
| `ChatCreated` | Чат создан | `chat_id`, `chat_type` |
| `ChatUpdated` | Чат обновлён | `chat_id`, `changed_fields` |
| `ChatMemberAdded` | Участник добавлен в чат | `chat_id`, `user_id` |
| `ChatMemberRemoved` | Участник удалён из чата | `chat_id`, `user_id` |
| `ChatMemberRoleChanged` | Роль участника изменена | `chat_id`, `user_id`, `new_role` |
| `ThreadCreated` | Тред создан | `thread_id`, `chat_id`, `parent_message_id` |
| `ThreadResolved` | Тред закрыт | `thread_id` |
| `ThreadReopened` | Тред открыт заново | `thread_id` |

### Comment Events

| Событие | Описание | Поля |
|---|---|---|
| `CommentAdded` | Комментарий добавлен | `comment_id`, `target_type`, `target_id`, `author_id` |
| `CommentUpdated` | Комментарий обновлён | `comment_id` |
| `CommentDeleted` | Комментарий удалён (soft) | `comment_id` |
| `CommentReplied` | Ответ на комментарий | `comment_id`, `parent_comment_id` |
| `CommentReactionAdded` | Реакция на комментарий | `comment_id`, `user_id`, `emoji` |
| `CommentReactionRemoved` | Реакция на комментарий снята | `comment_id`, `user_id`, `emoji` |
| `UserMentioned` | Пользователь упомянут | `mentioned_user_id`, `source_type`, `source_id` |

### Meeting Events

| Событие | Описание | Поля |
|---|---|---|
| `MeetingScheduled` | Совещание запланировано | `meeting_id`, `title`, `scheduled_at`, `meeting_type` |
| `MeetingUpdated` | Совещание обновлено | `meeting_id`, `changed_fields` |
| `MeetingCancelled` | Совещание отменено | `meeting_id` |
| `MeetingStarted` | Совещание начато | `meeting_id` |
| `MeetingCompleted` | Совещание завершено | `meeting_id` |
| `MeetingNoteAdded` | Заметка добавлена | `meeting_id`, `note_id` |
| `MeetingActionItemAdded` | Action item добавлен | `meeting_id`, `action_item_id` |
| `MeetingActionItemCompleted` | Action item завершён | `meeting_id`, `action_item_id` |
| `MeetingRSVPUpdated` | RSVP ответ обновлён | `meeting_id`, `user_id`, `rsvp_status` |
| `MeetingParticipantAdded` | Участник добавлен в совещание | `meeting_id`, `user_id` |
| `MeetingParticipantRemoved` | Участник удалён из совещания | `meeting_id`, `user_id` |
| `MeetingJoinRequested` | Запрос на подключение к конференции | `meeting_id`, `user_id`, `provider` |
| `RecurringMeetingCreated` | Повторяющееся совещание создано | `source_meeting_id`, `new_meeting_id` |

### Message Events

| Событие | Описание | Поля |
|---|---|---|
| `MessageSent` | Сообщение отправлено | `message_id`, `chat_id`, `sender_id`, `message_type` |
| `MessageUpdated` | Сообщение обновлено | `message_id` |
| `MessageDeleted` | Сообщение удалено (soft) | `message_id` |
| `MessageReactionAdded` | Реакция на сообщение | `message_id`, `user_id`, `emoji` |
| `MessageReactionRemoved` | Реакция на сообщение снята | `message_id`, `user_id`, `emoji` |

**Итого: 33 события**

---

## События, на которые подписывается Communication BC

Нет. Communication BC не подписывается на события других BC.

---

## Провайдеры конференций (ConferenceProviderPort)

Meeting-агрегат не знает конкретных провайдеров видеоконференций — он
хранит только значение ``ConferenceProvider`` и opaque ``conference_room_id``.
Вся логика создания комнат / генерации токенов инкапсулирована за
портом ``ConferenceProviderPort`` (см. ``app/context/communication/application/ports/integration/inboard/conference_provider_port.py``).

| Провайдер | Статус | Описание |
|---|---|---|
| `manual` | реализовано | Пользователь сам вставляет ссылку (Zoom/Telemost/Meet/Teams/кастом). Адаптер ничего не делает с внешней системой. |
| `internal` | задел (раскомментировать адаптер) | Встроенный WebRTC через LiveKit — требует LiveKit-сервер и TURN. |
| `zoom` | задел | OAuth + Zoom API. |
| `telemost` | задел | Yandex Telemost API. |
| `google_meet` | задел | Google Calendar API + meet link. |
| `teams` | задел | Microsoft Graph API. |

Новые провайдеры добавляются в `ConferenceProviderRegistry` в
`app/core/di/providers/communication_provider.py::create_conference_provider_registry`.
Домен и presentation слой при этом не меняются.

---

## Outboard-провайдер для Notification BC

| Порт | Метод | Назначение |
|---|---|---|
| `ChatMembersProvider` | `get_chat_member_ids(chat_id)` | Notification BC использует через inboard-адаптер ``ChatMembersPort`` для рассылки уведомлений при `MessageSent` / `ChatMemberAdded`. |
