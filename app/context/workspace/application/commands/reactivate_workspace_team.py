from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.exceptions.workspace_team_exceptions import WorkspaceTeamNotFoundException
from app.context.workspace.domain.repositories.workspace_team_repository import WorkspaceTeamRepository


class ReactivateWorkspaceTeamCommand(BaseCommand):
    """
    Команда реактивации команды workspace.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        team_id: ID команды.
    """

    caller_id: str
    team_id: str


class ReactivateWorkspaceTeamHandler(BaseCommandHandler[ReactivateWorkspaceTeamCommand, None]):
    """Обработчик реактивации команды workspace."""

    REQUIRED_PERMISSION = "teams.write"

    def __init__(
        self,
        team_repo: WorkspaceTeamRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._team_repo = team_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: ReactivateWorkspaceTeamCommand) -> None:
        team = await self._team_repo.get_by_id(Id.from_string(command.team_id))
        if team is None:
            raise WorkspaceTeamNotFoundException(command.team_id)

        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            workspace_id=team.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )

        team.reactivate()
        await self._team_repo.update(team)
        await self._event_bus.publish_all(team.clear_domain_events())
