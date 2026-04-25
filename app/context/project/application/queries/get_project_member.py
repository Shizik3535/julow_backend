from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.project_member_dto import ProjectMemberDTO
from app.context.project.application.exceptions.membership_app_exceptions import MemberNotInProjectException
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)
from app.context.project.domain.repositories.project_membership_repository import ProjectMembershipRepository


class GetProjectMemberQuery(BaseQuery):
    """Запрос получения конкретного участника проекта."""

    caller_id: str
    project_id: str
    user_id: str


class GetProjectMemberHandler(BaseQueryHandler[GetProjectMemberQuery, ProjectMemberDTO]):
    """Обработчик получения конкретного участника проекта."""

    REQUIRED_PERMISSION = "members.read"

    def __init__(self, membership_repo: ProjectMembershipRepository, permission_checker: ProjectPermissionCheckerPort) -> None:
        super().__init__()
        self._membership_repo = membership_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetProjectMemberQuery) -> ProjectMemberDTO:
        project_id = Id.from_string(query.project_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(query.caller_id),
            project_id=project_id,
            permission=self.REQUIRED_PERMISSION,
        )
        member = await self._membership_repo.get_member_by_project_and_user(
            project_id=project_id,
            user_id=Id.from_string(query.user_id),
        )
        if member is None:
            raise MemberNotInProjectException(query.user_id, query.project_id)

        return ProjectMemberDTO(
            id=str(member.id),
            user_id=str(member.user_id),
            role_id=str(member.role_id),
            joined_at=member.joined_at,
            is_active=member.is_active,
        )
