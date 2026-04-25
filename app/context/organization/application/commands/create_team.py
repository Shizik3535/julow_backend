from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.team_dto import TeamDTO
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.aggregates.team import Team
from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository
from app.context.organization.domain.repositories.team_repository import TeamRepository


class CreateTeamCommand(BaseCommand):
    """
    Команда создания команды.

    Атрибуты:
        org_id: ID организации.
        name: Название команды.
        lead_id: ID лидера команды.
    """

    caller_id: str
    org_id: str
    name: str
    lead_id: str | None = None


class CreateTeamHandler(BaseCommandHandler[CreateTeamCommand, TeamDTO]):
    """
    Обработчик создания команды.

    Создаёт Team AR, сохраняет.
    """

    REQUIRED_PERMISSION = "teams.write"

    def __init__(self, team_repo: TeamRepository, org_repo: OrganizationRepository, org_permission_checker: OrgPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._team_repo = team_repo
        self._org_repo = org_repo
        self._org_permission_checker = org_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: CreateTeamCommand) -> TeamDTO:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)

        org = await self._org_repo.get_by_id(org_id)
        if org is None:
            raise OrganizationNotFoundException(command.org_id)
        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)
        team = Team.create(
            org_id=Id.from_string(command.org_id),
            name=command.name,
            lead_id=Id.from_string(command.lead_id) if command.lead_id else None,
        )

        await self._team_repo.add(team)
        await self._event_bus.publish_all(team.clear_domain_events())

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
