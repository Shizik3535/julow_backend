from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.exceptions.sprint_exceptions import SprintNotFoundException
from app.context.project.domain.repositories.sprint_repository import SprintRepository
from app.context.project.domain.value_objects.sprint_goal import SprintGoal
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)


class UpdateSprintGoalCommand(BaseCommand):
    """
    Команда обновления цели спринта.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        sprint_id: ID спринта.
        goal: Новая цель.
    """

    caller_id: str
    sprint_id: str
    goal: str


class UpdateSprintGoalHandler(BaseCommandHandler[UpdateSprintGoalCommand, None]):
    """Обработчик обновления цели спринта."""


    REQUIRED_PERMISSION = "sprints.write"

    def __init__(self, sprint_repo: SprintRepository, permission_checker: ProjectPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._sprint_repo = sprint_repo
        self._event_bus = event_bus
        self._permission_checker = permission_checker

    async def handle(self, command: UpdateSprintGoalCommand) -> None:
        sprint = await self._sprint_repo.get_by_id(Id.from_string(command.sprint_id))
        if sprint is None:
            raise SprintNotFoundException(command.sprint_id)


        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=sprint.project_id,
            permission=self.REQUIRED_PERMISSION,
        )
        sprint.update_goal(SprintGoal(value=command.goal))
        await self._sprint_repo.update(sprint)
        await self._event_bus.publish_all(sprint.clear_domain_events())
