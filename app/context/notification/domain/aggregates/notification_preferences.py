from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.value_objects.notification_type import NotificationType
from app.context.notification.domain.value_objects.channel_type import ChannelType
from app.context.notification.domain.entities.do_not_disturb_schedule import DoNotDisturbSchedule
from app.context.notification.domain.entities.digest_config import DigestConfig
from app.context.notification.domain.events.notification_events import (
    NotificationPreferencesUpdated,
    DoNotDisturbEnabled,
    DoNotDisturbDisabled,
)


# Типы, которые нельзя полностью отключить через project overrides
_MANDATORY_TYPES: set[NotificationType] = {NotificationType.SECURITY, NotificationType.BILLING}

# Каналы по умолчанию для каждого типа
_DEFAULT_CHANNELS: dict[NotificationType, list[ChannelType]] = {
    NotificationType.TASK_ASSIGNED: [ChannelType.IN_APP],
    NotificationType.MENTIONED: [ChannelType.IN_APP, ChannelType.EMAIL],
    NotificationType.STATUS_CHANGED: [ChannelType.IN_APP],
    NotificationType.DEADLINE_APPROACHING: [ChannelType.IN_APP, ChannelType.EMAIL],
    NotificationType.OVERDUE_TASK: [ChannelType.IN_APP, ChannelType.EMAIL, ChannelType.PUSH],
    NotificationType.NEW_COMMENT: [ChannelType.IN_APP],
    NotificationType.WATCHER_UPDATED: [ChannelType.IN_APP],
    NotificationType.INVITED: [ChannelType.IN_APP, ChannelType.EMAIL],
    NotificationType.SPRINT_COMPLETED: [ChannelType.IN_APP],
    NotificationType.SYSTEM: [ChannelType.IN_APP],
    NotificationType.BILLING: [ChannelType.IN_APP, ChannelType.EMAIL],
    NotificationType.SECURITY: [ChannelType.IN_APP, ChannelType.EMAIL, ChannelType.PUSH],
}


@dataclass
class NotificationPreferences(AggregateRoot):
    """
    Корень агрегата настроек уведомлений (Notification BC).

    Атрибуты:
        user_id: ID пользователя.
        channel_preferences: Маппинг NotificationType → список ChannelType.
        dnd_schedule: Расписание «Не беспокоить».
        digest_config: Настройка дайджеста.
        project_overrides: Переопределения по проекту (project_id → {type → channels}).
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    user_id: Id = field(default_factory=Id.generate)
    channel_preferences: dict[NotificationType, list[ChannelType]] = field(default_factory=dict)
    dnd_schedule: DoNotDisturbSchedule | None = None
    digest_config: DigestConfig | None = None
    project_overrides: dict[Id, dict[NotificationType, list[ChannelType]]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    def __post_init__(self) -> None:
        if not self.channel_preferences:
            self.channel_preferences = dict(_DEFAULT_CHANNELS)

    @classmethod
    def create(cls, user_id: Id) -> NotificationPreferences:
        """Создаёт настройки с дефолтными каналами."""
        prefs = cls(user_id=user_id)
        return prefs

    def update_channels(self, channel_preferences: dict[NotificationType, list[ChannelType]]) -> None:
        """Обновляет каналы уведомлений."""
        # Проверяем, что обязательные типы не отключены
        for mandatory_type in _MANDATORY_TYPES:
            channels = channel_preferences.get(mandatory_type, [])
            if not channels:
                raise ValueError(f"Нельзя полностью отключить уведомления типа {mandatory_type.value}")
        self.channel_preferences = channel_preferences
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            NotificationPreferencesUpdated(user_id=str(self.user_id))
        )

    def enable_dnd(self, schedule: DoNotDisturbSchedule) -> None:
        """Включает DND расписание."""
        schedule.enabled = True
        self.dnd_schedule = schedule
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(DoNotDisturbEnabled(user_id=str(self.user_id)))

    def disable_dnd(self) -> None:
        """Отключает DND расписание."""
        if self.dnd_schedule is not None:
            self.dnd_schedule.enabled = False
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(DoNotDisturbDisabled(user_id=str(self.user_id)))

    def set_project_override(self, project_id: Id, preferences: dict[NotificationType, list[ChannelType]]) -> None:
        """Устанавливает переопределение каналов для проекта."""
        # Обязательные типы нельзя полностью отключить
        for mandatory_type in _MANDATORY_TYPES:
            channels = preferences.get(mandatory_type, [])
            if not channels:
                raise ValueError(f"Нельзя полностью отключить {mandatory_type.value} уведомления для проекта")
        self.project_overrides[project_id] = preferences
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            NotificationPreferencesUpdated(user_id=str(self.user_id))
        )

    def remove_project_override(self, project_id: Id) -> None:
        """Удаляет переопределение каналов для проекта."""
        self.project_overrides.pop(project_id, None)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            NotificationPreferencesUpdated(user_id=str(self.user_id))
        )
