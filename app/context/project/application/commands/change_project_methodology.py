from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.project.domain.repositories.sprint_repository import SprintRepository
from app.context.project.domain.value_objects.methodology import Methodology
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)


class ChangeProjectMethodologyCommand(BaseCommand):
    """
    Команда смены методологии проекта.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        project_id: ID проекта.
        new_methodology: Новая методология.
    """

    caller_id: str
    project_id: str
    new_methodology: str


class ChangeProjectMethodologyHandler(BaseCommandHandler[ChangeProjectMethodologyCommand, None]):
    """
    Обработчик смены методологии.

    Проверяет отсутствие активных спринтов через SprintRepository.
    """


    REQUIRED_PERMISSION = "project.settings.write"

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
    async def handle(self, command: ChangeProjectMethodologyCommand) -> None:
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
        has_active = len(active_sprints) > 0

        new_methodology = Methodology(command.new_methodology)
        project.change_methodology(new_methodology, has_active_sprints=has_active)
        await self._project_repo.update(project)
        await self._event_bus.publish_all(project.clear_domain_events())
