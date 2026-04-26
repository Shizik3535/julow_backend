from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.events.project_role_events import (
    ProjectRoleCreated,
    ProjectRoleUpdated,
    ProjectRoleDeleted,
)
from app.context.project.domain.exceptions.project_role_exceptions import (
    CannotDeleteSystemRoleException,
)


@dataclass
class ProjectRole(AggregateRoot):
    """
    Корень агрегата роли проекта (Project BC).

    Системные роли (owner, admin, manager, member, guest) — предустановленные
    записи с is_system=True. Кастомные роли создаются админами проекта.

    Атрибуты:
        project_id: Opaque ID проекта (None для системных).
        name: Название роли.
        permissions: Список разрешений.
        is_system: Является ли роль системной.
        description: Описание роли.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    project_id: Id | None = None
    name: str = ""
    permissions: list[str] = field(default_factory=list)
    is_system: bool = False
    description: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create_system(cls, name: str, permissions: list[str], description: str | None = None, project_id: Id | None = None) -> ProjectRole:
        """Создаёт системную роль (глобальную или привязанную к проекту)."""
        role = cls(name=name, permissions=permissions, is_system=True, description=description, project_id=project_id)
        role._register_event(ProjectRoleCreated(project_id=str(project_id) if project_id else "", role_name=name))
        return role

    @classmethod
    def create_custom(cls, project_id: Id, name: str, permissions: list[str], description: str | None = None) -> ProjectRole:
        """Создаёт кастомную роль для проекта."""
        role = cls(project_id=project_id, name=name, permissions=permissions, is_system=False, description=description)
        role._register_event(ProjectRoleCreated(project_id=str(project_id), role_name=name))
        return role

    def update(self, permissions: list[str] | None = None, description: str | None = None) -> None:
        if permissions is not None:
            self.permissions = permissions
        if description is not None:
            self.description = description
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ProjectRoleUpdated(
                project_id=str(self.project_id) if self.project_id else "",
                role_name=self.name,
            )
        )

    def can_be_deleted(self) -> bool:
        return not self.is_system

    def assert_deletable(self) -> None:
        if self.is_system:
            raise CannotDeleteSystemRoleException(role_name=self.name)

    def mark_deleted(self) -> None:
        self.assert_deletable()
        self._register_event(
            ProjectRoleDeleted(
                project_id=str(self.project_id) if self.project_id else "",
                role_name=self.name,
            )
        )
