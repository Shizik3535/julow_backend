from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.dto.workspace_team_dto import WorkspaceTeamDTO
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.exceptions.workspace_team_exceptions import WorkspaceTeamNotFoundException
from app.context.workspace.domain.repositories.workspace_team_repository import WorkspaceTeamRepository


class GetWorkspaceTeamQuery(BaseQuery):
    """
    Запрос команды workspace по ID.

    Атрибуты:
        caller_id: ID пользователя, выполняющего запрос.
        team_id: ID команды.
    """

    caller_id: str
    team_id: str


class GetWorkspaceTeamHandler(BaseQueryHandler[GetWorkspaceTeamQuery, WorkspaceTeamDTO]):
    """Обработчик запроса команды workspace по ID."""

    REQUIRED_PERMISSION = "teams.read"

    def __init__(
        self,
        team_repo: WorkspaceTeamRepository,
        permission_checker: WorkspacePermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._team_repo = team_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetWorkspaceTeamQuery) -> WorkspaceTeamDTO:
        team = await self._team_repo.get_by_id(Id.from_string(query.team_id))
        if team is None:
            raise WorkspaceTeamNotFoundException(query.team_id)

        await self._permission_checker.require_permission(
            user_id=Id.from_string(query.caller_id),
            workspace_id=team.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )

        return WorkspaceTeamDTO(
            id=str(team.id),
            workspace_id=str(team.workspace_id),
            name=team.name,
            description=team.description,
            lead_id=str(team.lead_id) if team.lead_id else None,
            member_ids=[str(mid) for mid in team.member_ids],
            icon_url=str(team.icon_url) if team.icon_url else None,
            is_active=team.is_active,
            created_at=team.created_at,
            updated_at=team.updated_at,
        )
