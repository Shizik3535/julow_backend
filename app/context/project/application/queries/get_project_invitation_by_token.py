from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.project_invitation_dto import ProjectInvitationDTO
from app.context.project.domain.exceptions.project_invitation_exceptions import (
    ProjectInvitationNotFoundException,
)
from app.context.project.domain.repositories.project_invitation_repository import (
    ProjectInvitationRepository,
)
from app.context.project.domain.repositories.project_repository import ProjectRepository


class GetProjectInvitationByTokenQuery(BaseQuery):
    """
    Запрос приглашения в проект по токену (ссылке/коду).

    Атрибуты:
        token: Значение токена.
    """

    token: str


class GetProjectInvitationByTokenHandler(
    BaseQueryHandler[GetProjectInvitationByTokenQuery, ProjectInvitationDTO]
):
    """Обработчик запроса приглашения по токену."""

    def __init__(
        self,
        invitation_repo: ProjectInvitationRepository,
        project_repo: ProjectRepository,
    ) -> None:
        super().__init__()
        self._invitation_repo = invitation_repo
        self._project_repo = project_repo

    async def handle(self, query: GetProjectInvitationByTokenQuery) -> ProjectInvitationDTO:
        invitation = await self._invitation_repo.get_by_token(query.token)
        if invitation is None:
            raise ProjectInvitationNotFoundException(query.token)

        project = await self._project_repo.get_by_id(invitation.project_id)
        project_name = project.name if project else None

        return ProjectInvitationDTO(
            id=str(invitation.id),
            project_id=str(invitation.project_id),
            workspace_id=str(invitation.workspace_id),
            email=str(invitation.email) if invitation.email else None,
            link=(
                {
                    "value": invitation.link.value,
                    "expires_at": invitation.link.expires_at.isoformat() if invitation.link.expires_at else None,
                    "max_uses": invitation.link.max_uses,
                    "used_count": invitation.link.used_count,
                }
                if invitation.link
                else None
            ),
            role_id=str(invitation.role_id),
            invited_by=str(invitation.invited_by),
            invited_at=invitation.invited_at,
            status=invitation.status.value,
            user_id=str(invitation.user_id) if invitation.user_id else None,
            project_name=project_name,
            created_at=invitation.created_at,
            updated_at=invitation.updated_at,
        )
