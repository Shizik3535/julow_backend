from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.dto.workspace_member_dto import WorkspaceMemberDTO, WorkspaceMemberListDTO
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.repositories.workspace_membership_repository import WorkspaceMembershipRepository


class GetWorkspaceMembersQuery(BaseQuery):
    """
    Запрос участников workspace.

    Атрибуты:
        caller_id: ID пользователя, выполняющего запрос.
        workspace_id: ID workspace.
    """

    caller_id: str
    workspace_id: str


class GetWorkspaceMembersHandler(BaseQueryHandler[GetWorkspaceMembersQuery, WorkspaceMemberListDTO]):
    """Обработчик запроса участников workspace."""

    REQUIRED_PERMISSION = "members.read"

    def __init__(
        self,
        membership_repo: WorkspaceMembershipRepository,
        permission_checker: WorkspacePermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._membership_repo = membership_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetWorkspaceMembersQuery) -> WorkspaceMemberListDTO:
        ws_id = Id.from_string(query.workspace_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(query.caller_id),
            workspace_id=ws_id,
            permission=self.REQUIRED_PERMISSION,
        )
        members = await self._membership_repo.get_members_by_workspace(ws_id)
        items = [
            WorkspaceMemberDTO(
                id=str(m.id),
                user_id=str(m.user_id),
                display_name=m.display_name,
                role_id=str(m.role_id),
                joined_at=m.joined_at,
                is_active=m.is_active,
                source=m.source.value,
                invited_by=str(m.invited_by) if m.invited_by else None,
            )
            for m in members
        ]
        return WorkspaceMemberListDTO(items=items, total=len(items))
