from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.exceptions.board_app_exceptions import BoardNotFoundException
from app.context.project.domain.repositories.board_repository import BoardRepository
from app.context.project.domain.value_objects.project_view_config import ProjectViewConfig
from app.context.project.domain.value_objects.view_type import ViewType
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)


class CreateProjectViewCommand(BaseCommand):
    """
    Команда создания представления проекта.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        project_id: ID проекта.
        name: Название представления.
        view_type: Тип представления (BOARD, LIST, TIMELINE, ...).
        is_shared: Общее ли представление.
        owner_id: ID владельца (None — общее).
        filters: Фильтры (list[dict]).
        sorting: Сортировка (list[dict]).
        grouping: Группировка.
    """

    caller_id: str
    project_id: str
    name: str
    view_type: str = "BOARD"
    is_shared: bool = True
    owner_id: str | None = None
    filters: list[dict] | None = None
    sorting: list[dict] | None = None
    grouping: str | None = None


class CreateProjectViewHandler(BaseCommandHandler[CreateProjectViewCommand, None]):
    """Обработчик создания представления проекта."""


    REQUIRED_PERMISSION = "views.write"

    def __init__(self, board_repo: BoardRepository, permission_checker: ProjectPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._board_repo = board_repo
        self._event_bus = event_bus
        self._permission_checker = permission_checker

    async def handle(self, command: CreateProjectViewCommand) -> None:
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=Id.from_string(command.project_id),
            permission=self.REQUIRED_PERMISSION,
        )
        board = await self._board_repo.get_by_project_id(Id.from_string(command.project_id))
        if board is None:
            raise BoardNotFoundException(command.project_id)

        config = ProjectViewConfig(
            view_type=ViewType(command.view_type),
        )
        owner_id = Id.from_string(command.owner_id) if command.owner_id else None

        board.create_view(
            name=command.name,
            config=config,
            is_shared=command.is_shared,
            owner_id=owner_id,
        )
        await self._board_repo.update(board)
        await self._event_bus.publish_all(board.clear_domain_events())
