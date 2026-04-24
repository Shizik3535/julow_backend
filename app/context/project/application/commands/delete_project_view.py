from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.exceptions.board_app_exceptions import BoardNotFoundException
from app.context.project.domain.repositories.board_repository import BoardRepository
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)


class DeleteProjectViewCommand(BaseCommand):
    """
    Команда удаления представления проекта.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        project_id: ID проекта.
        view_id: ID представления.
    """

    caller_id: str
    project_id: str
    view_id: str


class DeleteProjectViewHandler(BaseCommandHandler[DeleteProjectViewCommand, None]):
    """Обработчик удаления представления проекта."""


    REQUIRED_PERMISSION = "views.write"

    def __init__(self, board_repo: BoardRepository, permission_checker: ProjectPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._board_repo = board_repo
        self._event_bus = event_bus
        self._permission_checker = permission_checker

    async def handle(self, command: DeleteProjectViewCommand) -> None:
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=Id.from_string(command.project_id),
            permission=self.REQUIRED_PERMISSION,
        )
        board = await self._board_repo.get_by_project_id(Id.from_string(command.project_id))
        if board is None:
            raise BoardNotFoundException(command.project_id)

        board.delete_view(Id.from_string(command.view_id))
        await self._board_repo.update(board)
        await self._event_bus.publish_all(board.clear_domain_events())
