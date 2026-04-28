from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.dto.workspace_team_dto import WorkspaceTeamDTO, WorkspaceTeamListDTO
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from app.context.workspace.domain.repositories.workspace_team_repository import WorkspaceTeamRepository
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository


class GetWorkspaceTeamsQuery(BaseQuery):
    """
    Запрос команд workspace.

    Атрибуты:
        caller_id: ID пользователя, выполняющего запрос.
        workspace_id: ID workspace.
    """

    caller_id: str
    workspace_id: str


class GetWorkspaceTeamsHandler(BaseQueryHandler[GetWorkspaceTeamsQuery, WorkspaceTeamListDTO]):
    """Обработчик запроса команд workspace."""

    REQUIRED_PERMISSION = "teams.read"

    def __init__(
        self,
        team_repo: WorkspaceTeamRepository,
        ws_repo: WorkspaceRepository,
        permission_checker: WorkspacePermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._team_repo = team_repo
        self._ws_repo = ws_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetWorkspaceTeamsQuery) -> WorkspaceTeamListDTO:
        ws_id = Id.from_string(query.workspace_id)

        ws = await self._ws_repo.get_by_id(ws_id)
        if ws is None:
            raise WorkspaceNotFoundException(query.workspace_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(query.caller_id),
            workspace_id=ws_id,
            permission=self.REQUIRED_PERMISSION,
        )
        teams = await self._team_repo.get_by_workspace(ws_id)
        items = [
            WorkspaceTeamDTO(
                id=str(t.id),
                workspace_id=str(t.workspace_id),
                name=t.name,
                description=t.description,
                lead_id=str(t.lead_id) if t.lead_id else None,
                member_ids=[str(mid) for mid in t.member_ids],
                icon=t.icon if t.icon else None,
                is_active=t.is_active,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
            for t in teams
        ]
        return WorkspaceTeamListDTO(items=items, total=len(items))
