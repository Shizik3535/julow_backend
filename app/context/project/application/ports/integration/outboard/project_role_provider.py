from __future__ import annotations

from abc import ABC, abstractmethod

from app.context.project.application.dto.project_role_dto import ProjectRoleDTO


class ProjectRoleProvider(ABC):
    """
    Outboard-порт: предоставление данных ролей проекта другим BC.

    Task BC использует для:
    - Проверки permissions участника (ACL при операциях с задачами).
    - Получения роли участника.
    """

    @abstractmethod
    async def get_role(self, role_id: str) -> ProjectRoleDTO | None:
        """Получить роль по ID."""

    @abstractmethod
    async def get_roles_by_project(self, project_id: str) -> list[ProjectRoleDTO]:
        """Получить все роли проекта."""

    @abstractmethod
    async def has_permission(self, role_id: str, permission: str) -> bool:
        """Проверить, есть ли у роли конкретное разрешение."""
