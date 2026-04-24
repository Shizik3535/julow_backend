from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.dto.workspace_member_dto import WorkspaceMemberDTO
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.exceptions.workspace_membership_exceptions import WorkspaceMemberNotFoundException
from app.context.workspace.domain.repositories.workspace_membership_repository import WorkspaceMembershipRepository


class GetWorkspaceMemberQuery(BaseQuery):
    """
    Запрос участника workspace.

    Атрибуты:
        caller_id: ID пользователя, выполняющего запрос.
        workspace_id: ID workspace.
        user_id: ID пользователя.
    """

    caller_id: str
    workspace_id: str
    user_id: str


class GetWorkspaceMemberHandler(BaseQueryHandler[GetWorkspaceMemberQuery, WorkspaceMemberDTO]):
    """Обработчик запроса участника workspace."""

    REQUIRED_PERMISSION = "members.read"

    def __init__(
        self,
        membership_repo: WorkspaceMembershipRepository,
        permission_checker: WorkspacePermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._membership_repo = membership_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetWorkspaceMemberQuery) -> WorkspaceMemberDTO:
        ws_id = Id.from_string(query.workspace_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(query.caller_id),
            workspace_id=ws_id,
            permission=self.REQUIRED_PERMISSION,
        )
        member = await self._membership_repo.get_member_by_workspace_and_user(
            ws_id,
            Id.from_string(query.user_id),
        )
        if member is None:
            raise WorkspaceMemberNotFoundException(id=Id.from_string(query.user_id))

        return WorkspaceMemberDTO(
            id=str(member.id),
            user_id=str(member.user_id),
            display_name=member.display_name,
            role_id=str(member.role_id),
            joined_at=member.joined_at,
            is_active=member.is_active,
            source=member.source.value,
            invited_by=str(member.invited_by) if member.invited_by else None,
        )
