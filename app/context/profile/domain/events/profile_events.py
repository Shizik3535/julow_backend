from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.profile.domain.value_objects.pinned_target_type import PinnedTargetType


@dataclass(frozen=True)
class ProfileCreated(BaseDomainEvent):
    """Профиль создан (по событию из Identity)."""

    user_id: str = ""


@dataclass(frozen=True)
class ProfileDeleted(BaseDomainEvent):
    """Профиль удалён (по событию из Identity)."""

    user_id: str = ""


@dataclass(frozen=True)
class AppearanceSettingsChanged(BaseDomainEvent):
    """Настройки внешнего вида изменены."""

    user_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class LocalizationSettingsChanged(BaseDomainEvent):
    """Настройки локализации изменены."""

    user_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NavigationSettingsChanged(BaseDomainEvent):
    """Настройки навигации изменены."""

    user_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PrivacySettingsChanged(BaseDomainEvent):
    """Настройки приватности изменены."""

    user_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AvatarChanged(BaseDomainEvent):
    """Аватар изменён."""

    user_id: str = ""


@dataclass(frozen=True)
class PersonalInfoChanged(BaseDomainEvent):
    """Персональные данные изменены (bio, job_title, social_links)."""

    user_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class HotkeysChanged(BaseDomainEvent):
    """Горячие клавиши обновлены."""

    user_id: str = ""


@dataclass(frozen=True)
class PinnedItemAdded(BaseDomainEvent):
    """Элемент закреплён."""

    user_id: str = ""
    target_type: PinnedTargetType = PinnedTargetType.TASK
    target_id: str = ""


@dataclass(frozen=True)
class PinnedItemRemoved(BaseDomainEvent):
    """Элемент откреплён."""

    user_id: str = ""
    target_type: PinnedTargetType = PinnedTargetType.TASK
    target_id: str = ""


@dataclass(frozen=True)
class SidebarConfigUpdated(BaseDomainEvent):
    """Sidebar обновлён."""

    user_id: str = ""
