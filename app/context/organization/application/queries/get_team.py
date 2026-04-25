from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.team_dto import TeamDTO
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.exceptions.team_exceptions import TeamNotFoundException
from app.context.organization.domain.repositories.team_repository import TeamRepository


class GetTeamQuery(BaseQuery):
    """
    Запрос команды по ID.

    Атрибуты:
        team_id: Идентификатор команды.
    """

    caller_id: str
    org_id: str
    team_id: str


class GetTeamHandler(BaseQueryHandler[GetTeamQuery, TeamDTO]):
    """Обработчик запроса команды по ID."""

    REQUIRED_PERMISSION = "teams.read"

    def __init__(self, team_repo: TeamRepository, org_permission_checker: OrgPermissionCheckerPort) -> None:
        super().__init__()
        self._team_repo = team_repo
        self._org_permission_checker = org_permission_checker

    async def handle(self, query: GetTeamQuery) -> TeamDTO:
        team = await self._team_repo.get_by_id(Id.from_string(query.team_id))
        if team is None:
            raise TeamNotFoundException(query.team_id)

        await self._org_permission_checker.require_permission(
            Id.from_string(query.caller_id), Id.from_string(query.org_id), self.REQUIRED_PERMISSION,
        )

        return TeamDTO(
            id=str(team.id),
            org_id=str(team.org_id),
            name=team.name,
            description=team.description,
            lead_id=str(team.lead_id) if team.lead_id else None,
            member_ids=[str(mid) for mid in team.member_ids],
            icon_url=str(team.icon_url) if team.icon_url else None,
            is_active=team.is_active,
            created_at=team.created_at,
            updated_at=team.updated_at,
        )
