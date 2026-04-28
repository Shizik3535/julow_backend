from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.value_objects.notification_type import NotificationType
from app.context.notification.domain.value_objects.channel_type import ChannelType
from app.context.notification.domain.value_objects.preference_scope import PreferenceScope
from app.context.notification.domain.value_objects.notification_policy import NotificationPolicy
from app.context.notification.domain.entities.do_not_disturb_schedule import DoNotDisturbSchedule
from app.context.notification.domain.entities.digest_config import DigestConfig
from app.context.notification.domain.entities.preference_entry import PreferenceEntry
from app.context.notification.domain.events.notification_events import (
    NotificationPreferenceUpdated,
    DndSettingsUpdated,
    DigestSettingsUpdated,
    ReminderWindowUpdated,
)


@dataclass
class NotificationPreferences(AggregateRoot):
    """
    Корень агрегата настроек уведомлений (Notification BC).

    Атрибуты:
        user_id: ID пользователя.
        preferences: Список записей настроек (PreferenceEntry).
        dnd_schedule: Расписание «Не беспокоить».
        digest_config: Настройка дайджеста.
        policy: Политика уведомлений (обязательные типы, каналы по умолчанию).
        reminder_window_hours: Окно напоминания о дедлайне (в часах, по умолчанию 24).
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    user_id: Id = field(default_factory=Id.generate)
    preferences: list[PreferenceEntry] = field(default_factory=list)
    dnd_schedule: DoNotDisturbSchedule | None = None
    digest_config: DigestConfig | None = None
    policy: NotificationPolicy = field(default_factory=NotificationPolicy.default)
    reminder_window_hours: int = 24
    _skip_defaults: bool = field(default=False, repr=False)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    def __post_init__(self) -> None:
        if not self.preferences and not self._skip_defaults:
            self.preferences = self._build_default_preferences()

    @classmethod
    def create(cls, user_id: Id, policy: NotificationPolicy | None = None) -> NotificationPreferences:
        """Создаёт настройки с дефолтными каналами."""
        return cls(user_id=user_id, policy=policy or NotificationPolicy.default())

    def _build_default_preferences(self) -> list[PreferenceEntry]:
        """Строит список PreferenceEntry по умолчанию из политики."""
        entries: list[PreferenceEntry] = []
        for ntype, channels in self.policy.default_channels.items():
            for channel in channels:
                entries.append(PreferenceEntry(
                    notification_type=ntype,
                    channel=channel,
                    enabled=True,
                    scope=PreferenceScope.GLOBAL,
                    scope_id=None,
                ))
        return entries

    def set_preference(
        self,
        notification_type: NotificationType,
        channel: ChannelType,
        enabled: bool,
        scope: PreferenceScope = PreferenceScope.GLOBAL,
        scope_id: Id | None = None,
    ) -> None:
        """Устанавливает настройку для типа + канала + scope."""
        if scope != PreferenceScope.GLOBAL and scope_id is None:
            raise ValueError(f"scope_id обязателен для scope={scope.value}")

        # Проверяем, что обязательные типы не отключены полностью
        if not enabled and self.policy.is_mandatory(notification_type):
            self._assert_mandatory_channel_enabled(notification_type, channel, scope, scope_id)

        # Ищем существующую запись
        for entry in self.preferences:
            if (entry.notification_type == notification_type
                    and entry.channel == channel
                    and entry.scope == scope
                    and entry.scope_id == scope_id):
                entry.enabled = enabled
                self.updated_at = datetime.now(tz=timezone.utc)
                self._register_event(
                    NotificationPreferenceUpdated(
                        user_id=str(self.user_id),
                        notification_type=notification_type,
                        channel=channel,
                        enabled=enabled,
                        scope=scope,
                    )
                )
                return

        # Запись не найдена — создаём новую
        self.preferences.append(PreferenceEntry(
            notification_type=notification_type,
            channel=channel,
            enabled=enabled,
            scope=scope,
            scope_id=scope_id,
        ))
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            NotificationPreferenceUpdated(
                user_id=str(self.user_id),
                notification_type=notification_type,
                channel=channel,
                enabled=enabled,
                scope=scope,
            )
        )

    def should_deliver(
        self,
        notification_type: NotificationType,
        channel: ChannelType,
        scope_id: Id | None = None,
    ) -> bool:
        """Проверяет, нужно ли доставлять уведомление данного типа через канал."""
        # Ищем project/workspace override сначала
        if scope_id is not None:
            for scope in (PreferenceScope.PROJECT, PreferenceScope.WORKSPACE):
                for entry in self.preferences:
                    if (entry.notification_type == notification_type
                            and entry.channel == channel
                            and entry.scope == scope
                            and entry.scope_id == scope_id):
                        return entry.enabled

        # Глобальная настройка
        for entry in self.preferences:
            if (entry.notification_type == notification_type
                    and entry.channel == channel
                    and entry.scope == PreferenceScope.GLOBAL):
                return entry.enabled

        # Если явной настройки нет — fallback на каналы по умолчанию из политики
        default_channels = self.policy.get_default_channels(notification_type)
        return channel in default_channels

    def is_dnd_active(self, now: datetime) -> bool:
        """Проверяет, активен ли DND в данный момент."""
        if self.dnd_schedule is None:
            return False
        return self.dnd_schedule.is_active_at(now)

    def update_dnd(self, schedule: DoNotDisturbSchedule) -> None:
        """Обновляет расписание DND."""
        self.dnd_schedule = schedule
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            DndSettingsUpdated(
                user_id=str(self.user_id),
                enabled=schedule.enabled,
            )
        )

    def disable_dnd(self) -> None:
        """Отключает DND расписание."""
        if self.dnd_schedule is not None:
            self.dnd_schedule.enabled = False
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            DndSettingsUpdated(user_id=str(self.user_id), enabled=False)
        )

    def update_digest(self, config: DigestConfig) -> None:
        """Обновляет конфигурацию дайджеста."""
        self.digest_config = config
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            DigestSettingsUpdated(
                user_id=str(self.user_id),
                enabled=config.is_enabled,
                frequency=config.frequency,
            )
        )

    def set_reminder_window(self, hours: int) -> None:
        """Устанавливает окно напоминания о дедлайне (в часах)."""
        if hours < 1:
            raise ValueError("reminder_window_hours должен быть >= 1")
        if hours > 168:
            raise ValueError("reminder_window_hours должен быть <= 168 (7 дней)")
        self.reminder_window_hours = hours
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ReminderWindowUpdated(
                user_id=str(self.user_id),
                hours=hours,
            )
        )

    def _assert_mandatory_channel_enabled(
        self,
        notification_type: NotificationType,
        channel: ChannelType,
        scope: PreferenceScope,
        scope_id: Id | None,
    ) -> None:
        """Проверяет, что после отключения останется хотя бы один включённый канал для обязательного типа."""
        remaining_enabled = False
        for entry in self.preferences:
            if (entry.notification_type == notification_type
                    and entry.channel != channel
                    and entry.scope == scope
                    and entry.scope_id == scope_id
                    and entry.enabled):
                remaining_enabled = True
                break

        # Если среди явных записей не осталось включённых, проверяем default_channels из политики
        if not remaining_enabled:
            default_channels = self.policy.get_default_channels(notification_type)
            for ch in default_channels:
                if ch == channel:
                    continue
                # Проверяем, нет ли явной записи, отключающей этот дефолтный канал
                is_explicitly_disabled = any(
                    entry.notification_type == notification_type
                    and entry.channel == ch
                    and entry.scope == scope
                    and entry.scope_id == scope_id
                    and not entry.enabled
                    for entry in self.preferences
                )
                if not is_explicitly_disabled:
                    remaining_enabled = True
                    break

        if not remaining_enabled:
            raise ValueError(
                f"Нельзя полностью отключить уведомления типа {notification_type.value}"
            )
