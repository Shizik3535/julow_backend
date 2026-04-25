from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.project.domain.value_objects.milestone_status import MilestoneStatus
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)


class ChangeProjectMilestoneStatusCommand(BaseCommand):
    """
    Команда смены статуса milestone проекта.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        project_id: ID проекта.
        milestone_id: ID milestone.
        new_status: Новый статус (NOT_STARTED, IN_PROGRESS, COMPLETED, OVERDUE).
    """

    caller_id: str
    project_id: str
    milestone_id: str
    new_status: str


class ChangeProjectMilestoneStatusHandler(BaseCommandHandler[ChangeProjectMilestoneStatusCommand, None]):
    """Обработчик смены статуса milestone."""


    REQUIRED_PERMISSION = "milestones.write"

    def __init__(self, project_repo: ProjectRepository, permission_checker: ProjectPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._project_repo = project_repo
        self._event_bus = event_bus
        self._permission_checker = permission_checker

    async def handle(self, command: ChangeProjectMilestoneStatusCommand) -> None:
        project_id = Id.from_string(command.project_id)
        project = await self._project_repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundException(command.project_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=project_id,
            permission=self.REQUIRED_PERMISSION,
        )

        new_status = MilestoneStatus(command.new_status)
        project.change_milestone_status(Id.from_string(command.milestone_id), new_status)
        await self._project_repo.update(project)
        await self._event_bus.publish_all(project.clear_domain_events())
