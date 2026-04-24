from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_domain_event import BaseDomainEvent


@dataclass(frozen=True)
class OrgMemberJoined(BaseDomainEvent):
    """Участник присоединился к организации."""

    org_id: str = ""
    user_id: str = ""
    role_id: str = ""


@dataclass(frozen=True)
class OrgMemberDisplayNameChanged(BaseDomainEvent):
    """Отображаемое имя участника изменено."""

    org_id: str = ""
    user_id: str = ""
    display_name: str = ""


@dataclass(frozen=True)
class OrgMemberRoleChanged(BaseDomainEvent):
    """Роль участника изменена."""

    org_id: str = ""
    user_id: str = ""
    new_role_id: str = ""


@dataclass(frozen=True)
class OrgMemberRemoved(BaseDomainEvent):
    """Участник удалён из организации."""

    org_id: str = ""
    user_id: str = ""


@dataclass(frozen=True)
class OrgMemberDeactivated(BaseDomainEvent):
    """Участник деактивирован."""

    org_id: str = ""
    user_id: str = ""


@dataclass(frozen=True)
class OrgMemberReactivated(BaseDomainEvent):
    """Участник реактивирован."""

    org_id: str = ""
    user_id: str = ""
