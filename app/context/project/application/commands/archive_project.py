from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.project.domain.repositories.sprint_repository import SprintRepository
from app.context.project.domain.value_objects.sprint_status import SprintStatus
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)


class ArchiveProjectCommand(BaseCommand):
    """
    Команда архивирования проекта.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        project_id: ID проекта.
    """

    caller_id: str
    project_id: str


class ArchiveProjectHandler(BaseCommandHandler[ArchiveProjectCommand, None]):
    """
    Обработчик архивирования проекта.

    Проверяет отсутствие активных спринтов.
    """


    REQUIRED_PERMISSION = "project.*"

    def __init__(
        self,
        project_repo: ProjectRepository,
        sprint_repo: SprintRepository,
        permission_checker: ProjectPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._project_repo = project_repo
        self._sprint_repo = sprint_repo
        self._event_bus = event_bus
        self._permission_checker = permission_checker
    async def handle(self, command: ArchiveProjectCommand) -> None:
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=Id.from_string(command.project_id),
            permission=self.REQUIRED_PERMISSION,
        )
        project_id = Id.from_string(command.project_id)
        project = await self._project_repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundException(command.project_id)

        active_sprints = await self._sprint_repo.get_active_by_project(project_id)
        if active_sprints:
            from app.context.project.domain.exceptions.project_exceptions import (
                CannotChangeMethodologyWithActiveSprintsException,
            )
            raise CannotChangeMethodologyWithActiveSprintsException()

        project.archive()
        await self._project_repo.update(project)
        await self._event_bus.publish_all(project.clear_domain_events())
