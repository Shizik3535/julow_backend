from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.value_objects.member_source import MemberSource


@dataclass
class WorkspaceMember(BaseEntity):
    """
    Сущность участника workspace.

    Принадлежит агрегату WorkspaceMembership.

    Атрибуты:
        user_id: Opaque ID пользователя из Identity BC.
        display_name: Отображаемое имя в рамках workspace.
        role_id: Opaque ID роли (ссылка на WorkspaceRole AR).
        joined_at: Время присоединения.
        is_active: Активен ли участник.
        source: Источник участника.
        invited_by: ID пригласившего (None — для владельца при создании).
    """

    user_id: Id = field(default_factory=Id.generate)
    display_name: str | None = None
    role_id: Id = field(default_factory=Id.generate)
    joined_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    is_active: bool = True
    source: MemberSource = MemberSource.DIRECT
    invited_by: Id | None = None
