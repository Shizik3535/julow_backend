from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.color_vo import Color
from app.context.project.application.exceptions.board_app_exceptions import BoardNotFoundException
from app.context.project.domain.repositories.board_repository import BoardRepository
from app.context.project.domain.value_objects.wip_limit import WIPLimit
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)


class AddBoardColumnCommand(BaseCommand):
    """
    Команда добавления колонки на доску.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        project_id: ID проекта.
        name: Название колонки.
        color: Цвет (hex).
        wip_limit: WIP-лимит.
        status_mapping_id: ID связанного workflow-статуса.
    """

    caller_id: str
    project_id: str
    name: str
    color: str | None = None
    wip_limit: int | None = None
    status_mapping_id: str | None = None


class AddBoardColumnHandler(BaseCommandHandler[AddBoardColumnCommand, None]):
    """Обработчик добавления колонки на доску."""


    REQUIRED_PERMISSION = "workflow.write"

    def __init__(self, board_repo: BoardRepository, permission_checker: ProjectPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._board_repo = board_repo
        self._event_bus = event_bus
        self._permission_checker = permission_checker

    async def handle(self, command: AddBoardColumnCommand) -> None:
        board = await self._board_repo.get_by_project_id(Id.from_string(command.project_id))
        if board is None:
            raise BoardNotFoundException(command.project_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=board.project_id,
            permission=self.REQUIRED_PERMISSION,
        )

        color = Color(command.color) if command.color else None
        wip_limit = WIPLimit(value=command.wip_limit) if command.wip_limit is not None else None
        status_mapping = Id.from_string(command.status_mapping_id) if command.status_mapping_id else None

        board.add_column(name=command.name, color=color, wip_limit=wip_limit, status_mapping=status_mapping)
        await self._board_repo.update(board)
        await self._event_bus.publish_all(board.clear_domain_events())
