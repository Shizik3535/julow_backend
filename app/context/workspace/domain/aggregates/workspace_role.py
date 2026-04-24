from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.events.workspace_role_events import (
    WorkspaceRoleCreated,
    WorkspaceRoleUpdated,
    WorkspaceRoleDeleted,
)
from app.context.workspace.domain.exceptions.workspace_role_exceptions import (
    CannotDeleteSystemRoleException,
)


@dataclass
class WorkspaceRole(AggregateRoot):
    """
    Корень агрегата роли workspace (Workspace BC).

    Системные роли (owner, admin, moderator, member) — предустановленные
    записи с is_system=True. Кастомные роли создаются админами workspace
    с is_system=False. Это открывает RBAC на уровне workspace.

    Атрибуты:
        workspace_id: Opaque ID workspace (None для системных).
        name: Название роли.
        permissions: Список разрешений.
        is_system: Является ли роль системной.
        description: Описание роли.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    workspace_id: Id | None = None
    name: str = ""
    permissions: list[str] = field(default_factory=list)
    is_system: bool = False
    description: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    # --- Фабричные методы ---

    @classmethod
    def create_system(
        cls,
        name: str,
        permissions: list[str],
        description: str | None = None,
    ) -> WorkspaceRole:
        """Создаёт системную роль."""
        role = cls(
            name=name,
            permissions=permissions,
            is_system=True,
            description=description,
        )
        role._register_event(
            WorkspaceRoleCreated(workspace_id="", role_name=name)
        )
        return role

    @classmethod
    def create_custom(
        cls,
        workspace_id: Id,
        name: str,
        permissions: list[str],
        description: str | None = None,
    ) -> WorkspaceRole:
        """Создаёт кастомную роль для workspace."""
        role = cls(
            workspace_id=workspace_id,
            name=name,
            permissions=permissions,
            is_system=False,
            description=description,
        )
        role._register_event(
            WorkspaceRoleCreated(workspace_id=str(workspace_id), role_name=name)
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
            WorkspaceRoleUpdated(
                workspace_id=str(self.workspace_id) if self.workspace_id else "",
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
            WorkspaceRoleDeleted(
                workspace_id=str(self.workspace_id) if self.workspace_id else "",
                role_name=self.name,
            )
        )
