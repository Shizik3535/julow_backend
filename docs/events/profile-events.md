# События Profile BC

## События, которые отдаёт Profile BC

### Profile Events

| Событие | Описание | Поля |
|---|---|---|
| `ProfileCreated` | Профиль создан (по событию из Identity) | `user_id` |
| `ProfileDeleted` | Профиль удалён (по событию из Identity) | `user_id` |
| `AppearanceSettingsChanged` | Настройки внешнего вида изменены | `user_id`, `changed_fields` |
| `LocalizationSettingsChanged` | Настройки локализации изменены | `user_id`, `changed_fields` |
| `NavigationSettingsChanged` | Настройки навигации изменены | `user_id`, `changed_fields` |
| `NotificationSettingsChanged` | Настройки уведомлений изменены | `user_id`, `changed_fields` |
| `PrivacySettingsChanged` | Настройки приватности изменены | `user_id`, `changed_fields` |
| `AvatarChanged` | Аватар изменён | `user_id` |
| `PersonalInfoChanged` | Персональные данные изменены (bio, job_title, social_links) | `user_id`, `changed_fields` |
| `HotkeysChanged` | Горячие клавиши обновлены | `user_id` |
| `PinnedItemAdded` | Элемент закреплён | `user_id`, `target_type`, `target_id` |
| `PinnedItemRemoved` | Элемент откреплён | `user_id`, `target_type`, `target_id` |
| `SidebarConfigUpdated` | Sidebar обновлён | `user_id` |

**Итого: 13 событий**

---

## События, на которые подписывается Profile BC

| Обработчик | Источник (BC) | Событие | Топик | Описание |
|---|---|---|---|---|
| `OnUserRegisteredCreateProfile` | Identity BC | `UserRegistered` | `identity.events` | Создаёт профиль пользователя с настройками по умолчанию при регистрации. Идемпотентно — если профиль уже существует, пропускает. |
| `OnUserDeletedDeleteProfile` | Identity BC | `UserDeleted` | `identity.events` | Помечает профиль как удалённый при удалении аккаунта. Идемпотентно — если профиль не найден, логирует и пропускает. |

**Итого: 2 подписки** (обе из Identity BC)
