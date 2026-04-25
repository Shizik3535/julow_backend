from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.project_member_dto import ProjectMemberDTO, ProjectMemberListDTO
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)
from app.context.project.domain.entities.project_member import ProjectMember
from app.context.project.domain.repositories.project_membership_repository import ProjectMembershipRepository


class GetProjectMembersQuery(BaseQuery):
    """Запрос получения участников проекта."""

    caller_id: str
    project_id: str


class GetProjectMembersHandler(BaseQueryHandler[GetProjectMembersQuery, ProjectMemberListDTO]):
    """Обработчик получения участников проекта."""

    REQUIRED_PERMISSION = "members.read"

    def __init__(self, membership_repo: ProjectMembershipRepository, permission_checker: ProjectPermissionCheckerPort) -> None:
        super().__init__()
        self._membership_repo = membership_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetProjectMembersQuery) -> ProjectMemberListDTO:
        project_id = Id.from_string(query.project_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(query.caller_id),
            project_id=project_id,
            permission=self.REQUIRED_PERMISSION,
        )
        members = await self._membership_repo.get_members_by_project(project_id)
        items = [self._to_dto(m) for m in members]
        return ProjectMemberListDTO(items=items, total=len(items))

    @staticmethod
    def _to_dto(m: ProjectMember) -> ProjectMemberDTO:
        return ProjectMemberDTO(
            id=str(m.id),
            user_id=str(m.user_id),
            role_id=str(m.role_id),
            joined_at=m.joined_at,
            is_active=m.is_active,
        )
