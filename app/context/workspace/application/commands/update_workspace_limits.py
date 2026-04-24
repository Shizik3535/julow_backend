from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository
from app.context.workspace.domain.value_objects.workspace_limits import WorkspaceLimits


class UpdateWorkspaceLimitsCommand(BaseCommand):
    """
    Команда обновления лимитов workspace.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        workspace_id: ID workspace.
        max_projects: Максимум проектов.
        max_members: Максимум участников.
        max_storage_bytes: Максимум хранилища.
        max_file_size_bytes: Максимум размера файла.
        max_teams: Максимум команд.
    """

    caller_id: str
    workspace_id: str
    max_projects: int | None = None
    max_members: int | None = None
    max_storage_bytes: int | None = None
    max_file_size_bytes: int | None = None
    max_teams: int | None = None


class UpdateWorkspaceLimitsHandler(BaseCommandHandler[UpdateWorkspaceLimitsCommand, None]):
    """Обработчик обновления лимитов workspace."""

    REQUIRED_PERMISSION = "ws.settings.write"

    def __init__(
        self,
        ws_repo: WorkspaceRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._ws_repo = ws_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: UpdateWorkspaceLimitsCommand) -> None:
        ws_id = Id.from_string(command.workspace_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            workspace_id=ws_id,
            permission=self.REQUIRED_PERMISSION,
        )
        ws = await self._ws_repo.get_by_id(ws_id)
        if ws is None:
            raise WorkspaceNotFoundException(command.workspace_id)

        current = ws.limits
        limits = WorkspaceLimits(
            max_projects=command.max_projects if command.max_projects is not None else current.max_projects,
            max_members=command.max_members if command.max_members is not None else current.max_members,
            max_storage_bytes=command.max_storage_bytes if command.max_storage_bytes is not None else current.max_storage_bytes,
            max_file_size_bytes=command.max_file_size_bytes if command.max_file_size_bytes is not None else current.max_file_size_bytes,
            max_teams=command.max_teams if command.max_teams is not None else current.max_teams,
        )

        ws.update_limits(limits)
        await self._ws_repo.update(ws)
        await self._event_bus.publish_all(ws.clear_domain_events())
