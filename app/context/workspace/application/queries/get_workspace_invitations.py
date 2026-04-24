from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.dto.workspace_invitation_dto import (
    WorkspaceInvitationDTO,
    WorkspaceInvitationListDTO,
)
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.repositories.workspace_invitation_repository import WorkspaceInvitationRepository


class GetWorkspaceInvitationsQuery(BaseQuery):
    """
    Запрос приглашений workspace.

    Атрибуты:
        caller_id: ID пользователя, выполняющего запрос.
        workspace_id: ID workspace.
    """

    caller_id: str
    workspace_id: str


class GetWorkspaceInvitationsHandler(BaseQueryHandler[GetWorkspaceInvitationsQuery, WorkspaceInvitationListDTO]):
    """Обработчик запроса приглашений workspace."""

    REQUIRED_PERMISSION = "members.invite"

    def __init__(
        self,
        invitation_repo: WorkspaceInvitationRepository,
        permission_checker: WorkspacePermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._invitation_repo = invitation_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetWorkspaceInvitationsQuery) -> WorkspaceInvitationListDTO:
        ws_id = Id.from_string(query.workspace_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(query.caller_id),
            workspace_id=ws_id,
            permission=self.REQUIRED_PERMISSION,
        )
        invitations = await self._invitation_repo.get_by_workspace_id(ws_id)
        items = [
            WorkspaceInvitationDTO(
                id=str(inv.id),
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
                approved_by=str(inv.approved_by) if inv.approved_by else None,
                created_at=inv.created_at,
                updated_at=inv.updated_at,
            )
            for inv in invitations
        ]
        return WorkspaceInvitationListDTO(items=items, total=len(items))
