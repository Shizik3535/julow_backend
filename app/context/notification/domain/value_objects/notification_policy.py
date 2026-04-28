from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from app.shared.domain.base_value_object import ValueObject
from app.context.notification.domain.value_objects.notification_type import NotificationType
from app.context.notification.domain.value_objects.channel_type import ChannelType


@dataclass(frozen=True)
class NotificationPolicy(ValueObject):
    """
    Value Object политики уведомлений.

    Определяет обязательные типы и каналы по умолчанию.
    Вынесена из агрегата для централизации конфигурации.

    Атрибуты:
        mandatory_types: Типы, которые нельзя полностью отключить.
        default_channels: Каналы по умолчанию для каждого типа (scope=GLOBAL).
    """

    mandatory_types: frozenset[NotificationType] = field(default_factory=frozenset)
    default_channels: Mapping[NotificationType, tuple[ChannelType, ...]] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.default_channels, MappingProxyType):
            immutable = MappingProxyType({
                k: tuple(v) if not isinstance(v, tuple) else v
                for k, v in self.default_channels.items()
            })
            object.__setattr__(self, 'default_channels', immutable)

    @classmethod
    def default(cls) -> NotificationPolicy:
        """Создаёт политику с настройками по умолчанию."""
        return cls(
            mandatory_types=frozenset({
                NotificationType.SECURITY_NEW_DEVICE,
                NotificationType.SECURITY_PASSWORD_CHANGED,
                NotificationType.SECURITY_2FA_CHANGED,
                NotificationType.BILLING_PAYMENT_SUCCESS,
                NotificationType.BILLING_PAYMENT_FAILED,
                NotificationType.BILLING_TRIAL_ENDING,
                NotificationType.BILLING_QUOTA_WARNING,
            }),
            default_channels={
                NotificationType.TASK_ASSIGNED: (ChannelType.IN_APP, ChannelType.EMAIL),
                NotificationType.TASK_UNASSIGNED: (ChannelType.IN_APP,),
                NotificationType.MENTIONED: (ChannelType.IN_APP, ChannelType.EMAIL),
                NotificationType.TASK_STATUS_CHANGED: (ChannelType.IN_APP,),
                NotificationType.TASK_DUE_APPROACHING: (ChannelType.IN_APP, ChannelType.EMAIL),
                NotificationType.TASK_OVERDUE: (ChannelType.IN_APP, ChannelType.EMAIL, ChannelType.PUSH),
                NotificationType.TASK_COMMENT: (ChannelType.IN_APP,),
                NotificationType.TASK_UPDATED: (ChannelType.IN_APP,),
                NotificationType.TASK_DEADLINE_CHANGED: (ChannelType.IN_APP, ChannelType.EMAIL),
                NotificationType.PROJECT_DEADLINE_APPROACHING: (ChannelType.IN_APP, ChannelType.EMAIL),
                NotificationType.PROJECT_INVITATION: (ChannelType.IN_APP, ChannelType.EMAIL),
                NotificationType.WORKSPACE_INVITATION: (ChannelType.IN_APP, ChannelType.EMAIL),
                NotificationType.ORGANIZATION_INVITATION: (ChannelType.EMAIL,),
                NotificationType.SPRINT_COMPLETED: (ChannelType.IN_APP,),
                NotificationType.SPRINT_STARTED: (ChannelType.IN_APP,),
                NotificationType.MEETING_SCHEDULED: (ChannelType.IN_APP, ChannelType.EMAIL),
                NotificationType.MEETING_CANCELLED: (ChannelType.IN_APP, ChannelType.EMAIL),
                NotificationType.MEETING_REMINDER: (ChannelType.IN_APP, ChannelType.PUSH),
                NotificationType.BILLING_PAYMENT_SUCCESS: (ChannelType.EMAIL,),
                NotificationType.BILLING_PAYMENT_FAILED: (ChannelType.IN_APP, ChannelType.EMAIL),
                NotificationType.BILLING_TRIAL_ENDING: (ChannelType.IN_APP, ChannelType.EMAIL),
                NotificationType.BILLING_QUOTA_WARNING: (ChannelType.IN_APP,),
                NotificationType.SECURITY_NEW_DEVICE: (ChannelType.EMAIL,),
                NotificationType.SECURITY_PASSWORD_CHANGED: (ChannelType.EMAIL,),
                NotificationType.SECURITY_2FA_CHANGED: (ChannelType.EMAIL,),
                NotificationType.SYSTEM_MAINTENANCE: (ChannelType.IN_APP, ChannelType.EMAIL),
                NotificationType.TIME_REMINDER: (ChannelType.IN_APP, ChannelType.PUSH),
                NotificationType.WELCOME: (ChannelType.IN_APP, ChannelType.EMAIL),
            },
        )

    def is_mandatory(self, notification_type: NotificationType) -> bool:
        """Проверяет, является ли тип обязательным."""
        return notification_type in self.mandatory_types

    def get_default_channels(self, notification_type: NotificationType) -> list[ChannelType]:
        """Возвращает каналы по умолчанию для типа."""
        return list(self.default_channels.get(notification_type, (ChannelType.IN_APP,)))
