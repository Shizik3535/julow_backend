from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id


@dataclass
class OrgMember(BaseEntity):
    """
    Сущность участника организации.

    Принадлежит агрегату OrgMembership.

    Атрибуты:
        user_id: Opaque ID пользователя из Identity BC.
        display_name: Отображаемое имя в рамках организации.
        role_id: Opaque ID роли (ссылка на OrgRole AR).
        joined_at: Время присоединения.
        is_active: Активен ли участник.
        invited_by: ID пригласившего (None — для владельца при создании).
    """

    user_id: Id = field(default_factory=Id.generate)
    display_name: str | None = None
    role_id: Id = field(default_factory=Id.generate)
    joined_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    is_active: bool = True
    invited_by: Id | None = None
