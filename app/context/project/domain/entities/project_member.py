from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.value_objects.membership_type import MembershipType


@dataclass
class ProjectMember(BaseEntity):
    """
    Сущность участника проекта.

    Принадлежит агрегату ProjectMembership.

    Атрибуты:
        user_id: Opaque ID пользователя из Identity BC.
        role_id: Opaque ID роли (ссылка на ProjectRole AR).
        membership_type: Тип членства (STANDARD или GUEST).
        joined_at: Время присоединения.
        is_active: Активен ли участник.
    """

    user_id: Id = field(default_factory=Id.generate)
    role_id: Id = field(default_factory=Id.generate)
    membership_type: MembershipType = MembershipType.STANDARD
    joined_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    is_active: bool = True
