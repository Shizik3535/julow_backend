from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.exceptions.team_exceptions import TeamNotFoundException
from app.context.organization.domain.repositories.team_repository import TeamRepository


class UpdateTeamCommand(BaseCommand):
    """
    Команда обновления информации команды.

    Атрибуты:
        team_id: ID команды.
        name: Новое название.
        description: Новое описание.
        lead_id: Новый ID лидера.
        icon_url: Новый URL иконки.
    """

    caller_id: str
    org_id: str
    team_id: str
    name: str | None = None
    description: str | None = None
    lead_id: str | None = None
    icon_url: str | None = None


class UpdateTeamHandler(BaseCommandHandler[UpdateTeamCommand, None]):
    """
    Обработчик обновления информации команды.

    Загружает Team, вызывает update, сохраняет.
    """

    REQUIRED_PERMISSION = "teams.write"

    def __init__(self, team_repo: TeamRepository, org_permission_checker: OrgPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._team_repo = team_repo
        self._org_permission_checker = org_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: UpdateTeamCommand) -> None:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)

        team = await self._team_repo.get_by_id(Id.from_string(command.team_id))
        if team is None:
            raise TeamNotFoundException(command.team_id)
        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)

        team.update(
            name=command.name,
            description=command.description,
            lead_id=Id.from_string(command.lead_id) if command.lead_id else None,
            icon_url=Url(command.icon_url) if command.icon_url else None,
        )
        await self._team_repo.update(team)
        await self._event_bus.publish_all(team.clear_domain_events())
