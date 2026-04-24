from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.exceptions.sprint_exceptions import SprintNotFoundException
from app.context.project.domain.repositories.sprint_repository import SprintRepository
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)


class CompleteSprintCommand(BaseCommand):
    """
    Команда завершения спринта.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        sprint_id: ID спринта.
        incomplete_task_ids: ID незавершённых задач.
        next_sprint_id: ID следующего спринта (None → бэклог).
    """

    caller_id: str
    sprint_id: str
    incomplete_task_ids: list[str] | None = None
    next_sprint_id: str | None = None


class CompleteSprintHandler(BaseCommandHandler[CompleteSprintCommand, None]):
    """Обработчик завершения спринта."""


    REQUIRED_PERMISSION = "sprints.write"

    def __init__(self, sprint_repo: SprintRepository, permission_checker: ProjectPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._sprint_repo = sprint_repo
        self._event_bus = event_bus
        self._permission_checker = permission_checker

    async def handle(self, command: CompleteSprintCommand) -> None:
        sprint = await self._sprint_repo.get_by_id(Id.from_string(command.sprint_id))
        if sprint is None:
            raise SprintNotFoundException(command.sprint_id)


        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=sprint.project_id,
            permission=self.REQUIRED_PERMISSION,
        )
        incomplete_ids = [Id.from_string(tid) for tid in command.incomplete_task_ids] if command.incomplete_task_ids else None
        next_sprint_id = Id.from_string(command.next_sprint_id) if command.next_sprint_id else None

        sprint.complete(incomplete_task_ids=incomplete_ids, next_sprint_id=next_sprint_id)
        await self._sprint_repo.update(sprint)
        await self._event_bus.publish_all(sprint.clear_domain_events())
