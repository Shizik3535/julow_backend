from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.exceptions.team_exceptions import TeamNotFoundException
from app.context.organization.domain.repositories.team_repository import TeamRepository


class RemoveTeamMemberCommand(BaseCommand):
    """
    Команда удаления участника из команды.

    Атрибуты:
        team_id: ID команды.
        user_id: ID пользователя.
    """

    caller_id: str
    org_id: str
    team_id: str
    user_id: str


class RemoveTeamMemberHandler(BaseCommandHandler[RemoveTeamMemberCommand, None]):
    """
    Обработчик удаления участника из команды.

    Загружает Team, вызывает remove_member, сохраняет.
    """

    REQUIRED_PERMISSION = "teams.write"

    def __init__(self, team_repo: TeamRepository, org_permission_checker: OrgPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._team_repo = team_repo
        self._org_permission_checker = org_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: RemoveTeamMemberCommand) -> None:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)

        team = await self._team_repo.get_by_id(Id.from_string(command.team_id))
        if team is None:
            raise TeamNotFoundException(command.team_id)
        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)

        team.remove_member(Id.from_string(command.user_id))
        await self._team_repo.update(team)
        await self._event_bus.publish_all(team.clear_domain_events())
