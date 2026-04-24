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


class UpdateAutomationRuleCommand(BaseCommand):
    """
    Команда обновления правила автоматизации.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        project_id: ID проекта.
        rule_id: ID правила.
        is_enabled: Включить/выключить.
        action_params: Новые параметры действия.
    """

    caller_id: str
    project_id: str
    rule_id: str
    is_enabled: bool | None = None
    action_params: dict[str, str] | None = None


class UpdateAutomationRuleHandler(BaseCommandHandler[UpdateAutomationRuleCommand, None]):
    """Обработчик обновления правила автоматизации."""

    REQUIRED_PERMISSION = "automations.write"

    def __init__(self, board_repo: BoardRepository, permission_checker: ProjectPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._board_repo = board_repo
        self._event_bus = event_bus
        self._permission_checker = permission_checker

    async def handle(self, command: UpdateAutomationRuleCommand) -> None:
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=Id.from_string(command.project_id),
            permission=self.REQUIRED_PERMISSION,
        )
        board = await self._board_repo.get_by_project_id(Id.from_string(command.project_id))
        if board is None:
            raise BoardNotFoundException(command.project_id)

        board.update_automation_rule(
            rule_id=Id.from_string(command.rule_id),
            is_enabled=command.is_enabled,
            action_params=command.action_params,
        )
        await self._board_repo.update(board)
        await self._event_bus.publish_all(board.clear_domain_events())
