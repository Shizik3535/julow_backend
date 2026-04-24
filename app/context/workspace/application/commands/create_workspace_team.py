from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.dto.workspace_team_dto import WorkspaceTeamDTO
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.aggregates.workspace_team import WorkspaceTeam
from app.context.workspace.domain.repositories.workspace_team_repository import WorkspaceTeamRepository


class CreateWorkspaceTeamCommand(BaseCommand):
    """
    Команда создания команды workspace.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        workspace_id: ID workspace.
        name: Название команды.
        lead_id: ID лидера команды (опционально).
    """

    caller_id: str
    workspace_id: str
    name: str
    lead_id: str | None = None


class CreateWorkspaceTeamHandler(BaseCommandHandler[CreateWorkspaceTeamCommand, WorkspaceTeamDTO]):
    """Обработчик создания команды workspace."""

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

    async def handle(self, command: CreateWorkspaceTeamCommand) -> WorkspaceTeamDTO:
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            workspace_id=Id.from_string(command.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )
        team = WorkspaceTeam.create(
            workspace_id=Id.from_string(command.workspace_id),
            name=command.name,
            lead_id=Id.from_string(command.lead_id) if command.lead_id else None,
        )

        await self._team_repo.add(team)
        await self._event_bus.publish_all(team.clear_domain_events())

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
