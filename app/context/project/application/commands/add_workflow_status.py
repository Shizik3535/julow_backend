from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.color_vo import Color
from app.context.project.application.exceptions.board_app_exceptions import BoardNotFoundException
from app.context.project.domain.repositories.board_repository import BoardRepository
from app.context.project.domain.value_objects.workflow_status_category import WorkflowStatusCategory
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)


class AddWorkflowStatusCommand(BaseCommand):
    """
    Команда добавления статуса workflow.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        project_id: ID проекта.
        name: Название статуса.
        category: Категория (TODO, IN_PROGRESS, DONE, CANCELLED, BLOCKED, REVIEW).
        color: Цвет (hex).
        icon: Иконка.
        is_default: Статус по умолчанию.
    """

    caller_id: str
    project_id: str
    name: str
    category: str = "TODO"
    color: str | None = None
    icon: str | None = None
    is_default: bool = False


class AddWorkflowStatusHandler(BaseCommandHandler[AddWorkflowStatusCommand, None]):
    """Обработчик добавления статуса workflow."""


    REQUIRED_PERMISSION = "workflow.write"

    def __init__(self, board_repo: BoardRepository, permission_checker: ProjectPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._board_repo = board_repo
        self._event_bus = event_bus
        self._permission_checker = permission_checker

    async def handle(self, command: AddWorkflowStatusCommand) -> None:
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=Id.from_string(command.project_id),
            permission=self.REQUIRED_PERMISSION,
        )
        board = await self._board_repo.get_by_project_id(Id.from_string(command.project_id))
        if board is None:
            raise BoardNotFoundException(command.project_id)

        color = Color(command.color) if command.color else None
        board.add_workflow_status(
            name=command.name,
            color=color,
            icon=command.icon,
            category=WorkflowStatusCategory(command.category),
            is_default=command.is_default,
        )
        await self._board_repo.update(board)
        await self._event_bus.publish_all(board.clear_domain_events())
