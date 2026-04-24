from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.value_objects.org_role_scope import OrgRoleScope
from app.context.organization.domain.events.org_role_events import (
    OrgRoleCreated,
    OrgRoleUpdated,
    OrgRoleDeleted,
)
from app.context.organization.domain.exceptions.org_role_exceptions import (
    CannotDeleteSystemRoleException,
)


@dataclass
class OrgRole(AggregateRoot):
    """
    Корень агрегата роли организации (Organization BC).

    Системные роли (owner, admin, moderator, member) — предустановленные
    записи с is_system=True. Кастомные роли создаются админами организации
    с is_system=False. Это открывает RBAC на уровне организации.

    Атрибуты:
        org_id: Opaque ID организации (пустой для системных ролей).
        name: Название роли.
        permissions: Список разрешений.
        is_system: Является ли роль системной.
        description: Описание роли.
        scope: Область действия роли.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    org_id: Id | None = None
    name: str = ""
    permissions: list[str] = field(default_factory=list)
    is_system: bool = False
    description: str | None = None
    scope: OrgRoleScope = OrgRoleScope.ORG
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    # --- Фабричные методы ---

    @classmethod
    def create_system(
        cls,
        name: str,
        permissions: list[str],
        scope: OrgRoleScope,
        description: str | None = None,
    ) -> OrgRole:
        """Создаёт системную роль."""
        role = cls(
            name=name,
            permissions=permissions,
            is_system=True,
            description=description,
            scope=scope,
        )
        role._register_event(
            OrgRoleCreated(org_id="", role_name=name)
        )
        return role

    @classmethod
    def create_custom(
        cls,
        org_id: Id,
        name: str,
        permissions: list[str],
        scope: OrgRoleScope,
        description: str | None = None,
    ) -> OrgRole:
        """Создаёт кастомную роль для организации."""
        role = cls(
            org_id=org_id,
            name=name,
            permissions=permissions,
            is_system=False,
            description=description,
            scope=scope,
        )
        role._register_event(
            OrgRoleCreated(org_id=str(org_id), role_name=name)
        )
        return role

    # --- Бизнес-методы ---

    def update(self, permissions: list[str] | None = None, description: str | None = None) -> None:
        """Обновляет роль."""
        if permissions is not None:
            self.permissions = permissions
        if description is not None:
            self.description = description
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            OrgRoleUpdated(
                org_id=str(self.org_id) if self.org_id else "",
                role_name=self.name,
            )
        )

    def can_be_deleted(self) -> bool:
        """Проверяет, можно ли удалить роль."""
        return not self.is_system

    def assert_deletable(self) -> None:
        """Проверяет, что роль можно удалить, иначе бросает исключение."""
        if self.is_system:
            raise CannotDeleteSystemRoleException(role_name=self.name)

    def mark_deleted(self) -> None:
        """Помечает роль как удалённую (порождает событие)."""
        self.assert_deletable()
        self._register_event(
            OrgRoleDeleted(
                org_id=str(self.org_id) if self.org_id else "",
                role_name=self.name,
            )
        )
