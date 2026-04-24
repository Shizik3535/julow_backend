from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_aggregate import AggregateRoot


@dataclass
class Role(AggregateRoot):
    """
    Корень агрегата роли пользователя (Identity BC).

    Системные роли (super_admin, admin, supporter, user) — предустановленные
    записи с is_system=True. Кастомные роли создаются через Administration BC
    с is_system=False. Это открывает RBAC без изменения домена.

    Как AggregateRoot, Role управляет своей собственной консистентностью
    и может порождать доменные события (RoleCreated, RoleModified, etc.)

    Атрибуты:
        name: Название роли (уникальное).
        permissions: Список разрешений роли.
        is_system: Является ли роль системной (неудаляемой).
        description: Описание роли.
    """

    name: str = ""
    permissions: list[str] = field(default_factory=list)
    is_system: bool = False
    description: str | None = None
