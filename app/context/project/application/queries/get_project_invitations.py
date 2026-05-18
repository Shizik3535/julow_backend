from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.project_invitation_dto import (
    ProjectInvitationDTO,
    ProjectInvitationListDTO,
)
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from app.context.project.domain.repositories.project_invitation_repository import (
    ProjectInvitationRepository,
)
from app.context.project.domain.repositories.project_repository import ProjectRepository


class GetProjectInvitationsQuery(BaseQuery):
    """
    Запрос приглашений проекта.

    Атрибуты:
        caller_id: ID пользователя, выполняющего запрос.
        project_id: ID проекта.
    """

    caller_id: str
    project_id: str


class GetProjectInvitationsHandler(
    BaseQueryHandler[GetProjectInvitationsQuery, ProjectInvitationListDTO],
):
    """Обработчик запроса приглашений проекта."""

    REQUIRED_PERMISSION = "members.read"

    def __init__(
        self,
        invitation_repo: ProjectInvitationRepository,
        project_repo: ProjectRepository,
        permission_checker: ProjectPermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._invitation_repo = invitation_repo
        self._project_repo = project_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetProjectInvitationsQuery) -> ProjectInvitationListDTO:
        project_id = Id.from_string(query.project_id)

        project = await self._project_repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundException(query.project_id)

        await self._permission_checker.require_permission(
            user_id=Id.from_string(query.caller_id),
            project_id=project_id,
            permission=self.REQUIRED_PERMISSION,
        )

        invitations = await self._invitation_repo.get_by_project_id(project_id)
        items = [
            ProjectInvitationDTO(
                id=str(inv.id),
                project_id=str(inv.project_id),
                workspace_id=str(inv.workspace_id),
                email=str(inv.email) if inv.email else None,
                link=(
                    {
                        "value": inv.link.value,
                        "expires_at": inv.link.expires_at.isoformat() if inv.link.expires_at else None,
                        "max_uses": inv.link.max_uses,
                        "used_count": inv.link.used_count,
                    }
                    if inv.link
                    else None
                ),
                role_id=str(inv.role_id),
                invited_by=str(inv.invited_by),
                invited_at=inv.invited_at,
                status=inv.status.value,
                user_id=str(inv.user_id) if inv.user_id else None,
                project_name=project.name,
                created_at=inv.created_at,
                updated_at=inv.updated_at,
            )
            for inv in invitations
        ]
        return ProjectInvitationListDTO(items=items, total=len(items))
