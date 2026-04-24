# Profile BC — Спецификация

> Путь: `app/context/profile/domain`
> Исходные требования: §13 (Персонализация), §17 (Локализация)

## Контекст

Profile BC отвечает за пользовательский профиль и настройки: персональные данные, внешний вид, локализацию, навигацию, горячие клавиши, уведомления и приватность. Профиль создаётся по событию `UserRegistered` из Identity BC.

---

## Принципы расширяемости

1. **Стабильные множества — enum, расширяемые — string с валидацией** — `Theme`, `TimeFormat`, `InterfaceDensity`, `WeekStartDay` стабильны → enum. `StartPage`, `DateFormat` будут расти → string с паттерном.
2. **Настройки сгруппированы в VO** — вместо N полей на AR — несколько VO-групп. Добавление настройки = поле в VO, не новый метод на AR.
3. **Нет UserStatus** — статус аккаунта принадлежит Identity BC (`AccountStatus`). Profile BC не дублирует.
4. **Типизированные ссылки** — `PinnedTargetType` enum вместо магических строк. `HotkeyAction` enum вместо `action: str`.
5. **Events по группам** — одно событие на группу настроек, с `changed_fields` для детализации. Добавление поля в группу не требует нового event.

---

## Value Objects

### Общие

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `AccentColor` | frozen dataclass | hex: str (validated #RRGGBB) | §13.1 |
| `CustomTheme` | frozen dataclass | name: str, colors: dict[str, AccentColor] (background, surface, text, primary, etc.) | §13.1 |
| `PinnedTargetType` | Enum | `WORKSPACE`, `PROJECT`, `TASK`, `DASHBOARD`, `REPORT` | §13.1 |
| `HotkeyAction` | Enum | `CREATE_TASK`, `NAVIGATE_INBOX`, `SEARCH`, `TOGGLE_SIDEBAR`, `GO_HOME`, `QUICK_ACTION` | §13.1 |
| `HotkeyConfig` | frozen dataclass | action: HotkeyAction, key_combination: str, is_enabled: bool | §13.1 |
| `SidebarSection` | frozen dataclass | section_id: str, is_collapsed: bool, item_ids: list[Id], order: int | §13.1 |

> **`PinnedTargetType`** — enum, т.к. типы закрепляемых сущностей привязаны к BC-моделям и стабильны. Добавление нового BC → новое значение.
>
> **`HotkeyAction`** — enum для типобезопасности. Новые действия добавляются по мере развития UI.
>
> **`SidebarSection`** — гибкая модель sidebar: произвольные секции с элементами, сворачиваемые, с порядком.

### AppearanceSettings (VO group)

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `Theme` | Enum | `LIGHT`, `DARK`, `SYSTEM`, `CUSTOM` | §13.1 |
| `InterfaceDensity` | Enum | `COMPACT`, `COMFORTABLE`, `SPACIOUS` | §13.1 |

> `Theme.CUSTOM` активирует `CustomTheme` в `AppearanceSettings`.

### LocalizationSettings (VO group)

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `DateFormat` | str (validated pattern) | Паттерн: `"DD.MM.YYYY"`, `"MM/DD/YYYY"`, `"YYYY-MM-DD"`, `"DD/MM/YYYY"`, `"YYYY/MM/DD"` и др. Валидация по regex `^[DMY]{2}[./\-][DMY]{2}[./\-][DMY]{4}$` | §13.1 |
| `TimeFormat` | Enum | `H24`, `H12` | §13.1 |
| `WeekStartDay` | Enum | `MONDAY`, `SUNDAY`, `SATURDAY` | §13.1 |

> **`DateFormat` как string** — форматов дат может быть сколь угодно много (локали). Валидация через паттерн, а не enum. Предустановленные паттерны доступны как константы на app-слое.

### NavigationSettings (VO group)

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `StartPage` | str (validated identifier) | Идентификатор страницы: `"my_tasks"`, `"dashboard"`, `"inbox"`, `"calendar"`, `"reports"`, `"team"`. Валидация: непустая строка, зарегистрированные страницы проверяются на app-слое | §13.1 |

> **`StartPage` как string** — новые разделы приложения появляются часто. Строка с валидацией на app-слое (проверка что страница существует) вместо enum.

### NotificationSettings (VO group)

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `NotificationChannel` | Enum | `IN_APP`, `EMAIL`, `PUSH`, `SMS` | §10 |
| `NotificationType` | Enum | `TASK_ASSIGNED`, `TASK_UPDATED`, `MENTION`, `COMMENT_ADDED`, `MEETING_REMINDER`, `SYSTEM_ANNOUNCEMENT`, `DEADLINE_APPROACHING` | §10 |
| `ChannelPreference` | frozen dataclass | channel: NotificationChannel, is_enabled: bool | §10 |
| `TypePreference` | frozen dataclass | notification_type: NotificationType, channels: list[ChannelPreference], is_enabled: bool | §10 |

> **`NotificationType`** — будет расти по мере добавления новых типов событий в системе. Новое значение = правка enum + миграция, процедура аналогична `AuthProvider` из Identity BC.

### PrivacySettings (VO group)

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `ProfileVisibility` | Enum | `PUBLIC`, `ORGANIZATION_ONLY`, `PRIVATE` | §13 |
| `OnlineStatusVisibility` | Enum | `EVERYONE`, `CONTACTS_ONLY`, `NOBODY` | §13 |
| `ActivityTrackingConsent` | Enum | `GRANTED`, `DENIED` | §13 |

## Entities

| Сущность | Поля | Описание | Исходное требование |
|---|---|---|---|
| `PinnedItem` | target_type: PinnedTargetType, target_id: Id, order: int, pinned_at: datetime | Закреплённый элемент | §13.1 |
| `SocialLink` | platform: str, url: Url, display_name: str \| None | Социальная ссылка пользователя | §13 |

## Domain Events

| Событие | Поля | Описание | Исходное требование |
|---|---|---|---|
| `ProfileCreated` | user_id | Профиль создан (по событию из Identity) | — |
| `ProfileDeleted` | user_id | Профиль удалён (по событию из Identity) | — |
| `AppearanceSettingsChanged` | user_id, changed_fields: list[str] | Настройки внешнего вида изменены | §13.1 |
| `LocalizationSettingsChanged` | user_id, changed_fields: list[str] | Настройки локализации изменены | §13.1, §17 |
| `NavigationSettingsChanged` | user_id, changed_fields: list[str] | Настройки навигации изменены | §13.1 |
| `NotificationSettingsChanged` | user_id, changed_fields: list[str] | Настройки уведомлений изменены | §10 |
| `PrivacySettingsChanged` | user_id, changed_fields: list[str] | Настройки приватности изменены | §13 |
| `AvatarChanged` | user_id | Аватар изменён | §13.1 |
| `PersonalInfoChanged` | user_id, changed_fields: list[str] | Персональные данные изменены (bio, job_title, social_links) | §13 |
| `HotkeysChanged` | user_id | Горячие клавиши обновлены | §13.1 |
| `PinnedItemAdded` | user_id, target_type, target_id | Элемент закреплён | §13.1 |
| `PinnedItemRemoved` | user_id, target_type, target_id | Элемент откреплён | §13.1 |
| `SidebarConfigUpdated` | user_id | Sidebar обновлён | §13.1 |

> **`changed_fields`** — список имён изменённых полей внутри группы. Например, `AppearanceSettingsChanged(changed_fields=["theme", "accent_color"])`. Это позволяет UI реагировать точечно, не создавая отдельный event на каждое поле. Добавление нового поля в VO-группу не требует нового event.

## Exceptions

| Исключение | Описание |
|---|---|
| `ProfileNotFoundException` | Профиль не найден |
| `InvalidAccentColorException` | Некорректный формат цвета |
| `InvalidHotkeyException` | Некорректная комбинация клавиш или неизвестный action |
| `InvalidDateFormatException` | Некорректный паттерн формата даты |
| `InvalidStartPageException` | Некорректный идентификатор стартовой страницы |
| `DuplicatePinnedItemException` | Элемент уже закреплён |
| `DuplicateSocialLinkException` | Социальная ссылка с таким platform уже существует |
| `InvalidUrlException` | Некорректный URL |

## Aggregates

### UserProfile (Aggregate Root)

Один AR на пользователя. Настройки организованы в VO-группы — добавление новой настройки = поле в VO, а не новый метод на AR.

Поля:
- user_id: Id (opaque, из Identity BC)
- avatar_url: Url | None
- bio: str | None
- job_title: str | None
- social_links: list[SocialLink]
- appearance: AppearanceSettings
- localization: LocalizationSettings
- navigation: NavigationSettings
- notifications: NotificationSettings
- privacy: PrivacySettings
- hotkeys: list[HotkeyConfig]
- sidebar_sections: list[SidebarSection]
- pinned_items: list[PinnedItem]
- created_at: datetime
- updated_at: datetime

Методы:
- `create(user_id)` → `UserProfile` (factory, все настройки по умолчанию)
- `change_avatar(url)`
- `update_personal_info(bio=None, job_title=None)` → изменяет только переданные поля
- `add_social_link(platform, url, display_name=None)`
- `remove_social_link(platform)`
- `update_appearance(settings: AppearanceSettings)` → заменяет всю группу или часть
- `update_localization(settings: LocalizationSettings)`
- `update_navigation(settings: NavigationSettings)`
- `update_notifications(settings: NotificationSettings)`
- `update_privacy(settings: PrivacySettings)`
- `update_hotkeys(configs: list[HotkeyConfig])`
- `update_sidebar(sections: list[SidebarSection])`
- `pin_item(target_type, target_id)`
- `unpin_item(target_type, target_id)`
- `reorder_pinned_items(ordered_ids: list[Id])`

Инварианты:
- Один пользователь — один профиль
- Pinned items уникальны по (target_type, target_id)
- Social links уникальны по platform
- Хотя бы один `ChannelPreference` включён для каждого `TypePreference` если `is_enabled=True`
- `ProfileVisibility.ORGANIZATION_ONLY` требует membership (проверка на app-слое через ACL)

### AppearanceSettings (Value Object Group)

Поля:
- theme: Theme
- accent_color: AccentColor
- custom_theme: CustomTheme | None
- interface_density: InterfaceDensity

### LocalizationSettings (Value Object Group)

Поля:
- language: LanguageCode (из shared)
- timezone: Timezone (из shared)
- date_format: DateFormat
- time_format: TimeFormat
- week_start_day: WeekStartDay

### NavigationSettings (Value Object Group)

Поля:
- start_page: StartPage

### NotificationSettings (Value Object Group)

Поля:
- type_preferences: list[TypePreference]

### PrivacySettings (Value Object Group)

Поля:
- profile_visibility: ProfileVisibility
- online_status_visibility: OnlineStatusVisibility
- activity_tracking_consent: ActivityTrackingConsent

> **Добавление новой настройки**: (1) добавить поле в соответствующую VO-группу, (2) обновить дефолт в factory, (3) при необходимости — миграцию БД. Новый event не нужен — групповой event уже покрывает. Новая группа настроек — добавить VO-группу + поле на AR.

## Repositories

| Репозиторий | Методы |
|---|---|
| `UserProfileRepository` | `get_by_user_id`, `get_by_id`, `search`, `get_by_role` (для administration) |

## Значения по умолчанию

При создании профиля (factory `create`):

| Группа | Значения по умолчанию |
|---|---|
| AppearanceSettings | theme=SYSTEM, accent_color=#6366F1, interface_density=COMFORTABLE, custom_theme=None |
| LocalizationSettings | language=en, timezone=UTC, date_format=YYYY-MM-DD, time_format=H24, week_start_day=MONDAY |
| NavigationSettings | start_page=dashboard |
| NotificationSettings | все типы включены, каналы: IN_APP + EMAIL включены, PUSH + SMS выключены |
| PrivacySettings | profile_visibility=ORGANIZATION_ONLY, online_status_visibility=EVERYONE, activity_tracking_consent=GRANTED |

> Дефолты могут переопределяться на app-слое на основе контекста (организация, регион).
