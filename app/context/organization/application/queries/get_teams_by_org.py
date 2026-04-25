from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.team_dto import TeamDTO, TeamListDTO
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository
from app.context.organization.domain.repositories.team_repository import TeamRepository


class GetTeamsByOrgQuery(BaseQuery):
    """
    Запрос списка команд организации.

    Атрибуты:
        org_id: ID организации.
    """

    caller_id: str
    org_id: str


class GetTeamsByOrgHandler(BaseQueryHandler[GetTeamsByOrgQuery, TeamListDTO]):
    """Обработчик запроса списка команд организации."""

    REQUIRED_PERMISSION = "teams.read"

    def __init__(self, team_repo: TeamRepository, org_repo: OrganizationRepository, org_permission_checker: OrgPermissionCheckerPort) -> None:
        super().__init__()
        self._team_repo = team_repo
        self._org_repo = org_repo
        self._org_permission_checker = org_permission_checker

    async def handle(self, query: GetTeamsByOrgQuery) -> TeamListDTO:
        org_id = Id.from_string(query.org_id)

        org = await self._org_repo.get_by_id(org_id)
        if org is None:
            raise OrganizationNotFoundException(query.org_id)
        await self._org_permission_checker.require_permission(
            Id.from_string(query.caller_id), org_id, self.REQUIRED_PERMISSION,
        )

        teams = await self._team_repo.get_by_org(org_id)

        items = [
            TeamDTO(
                id=str(t.id),
                org_id=str(t.org_id),
                name=t.name,
                description=t.description,
                lead_id=str(t.lead_id) if t.lead_id else None,
                member_ids=[str(mid) for mid in t.member_ids],
                icon_url=str(t.icon_url) if t.icon_url else None,
                is_active=t.is_active,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
            for t in teams
        ]
        return TeamListDTO(items=items, total=len(items))
