from __future__ import annotations

from app.context.project.application.dto.project_role_dto import ProjectRoleDTO
from app.context.project.application.ports.integration.outboard.project_role_provider import (
    ProjectRoleProvider,
)
from app.context.project.domain.repositories.project_role_repository import ProjectRoleRepository
from app.shared.domain.value_objects.id_vo import Id


class ProjectRoleProviderAdapter(ProjectRoleProvider):
    """
    Реализация outboard-порта ProjectRoleProvider.

    Делегирует в ProjectRoleRepository для предоставления
    данных ролей проекта другим BC.
    """

    def __init__(self, repo: ProjectRoleRepository) -> None:
        self._repo = repo

    async def get_role(self, role_id: str) -> ProjectRoleDTO | None:
        role = await self._repo.get_by_id(Id.from_string(role_id))
        if role is None:
            return None
        return self._to_dto(role)

    async def get_roles_by_project(self, project_id: str) -> list[ProjectRoleDTO]:
        roles = await self._repo.get_by_project(Id.from_string(project_id))
        return [self._to_dto(r) for r in roles]

    async def has_permission(self, role_id: str, permission: str) -> bool:
        role = await self._repo.get_by_id(Id.from_string(role_id))
        if role is None:
            return False
        return permission in role.permissions

    @staticmethod
    def _to_dto(role) -> ProjectRoleDTO:
        return ProjectRoleDTO(
            id=str(role.id),
            project_id=str(role.project_id) if role.project_id else "",
            name=role.name,
            permissions=list(role.permissions),
            is_system=role.is_system,
            description=role.description,
            created_at=role.created_at,
            updated_at=role.updated_at,
        )
