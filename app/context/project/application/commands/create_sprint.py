from __future__ import annotations

from datetime import date

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.date_range_vo import DateRange
from app.context.project.application.dto.sprint_dto import SprintDTO
from app.context.project.application.exceptions.sprint_app_exceptions import SprintCapabilityNotAvailableException
from app.context.project.domain.aggregates.sprint import Sprint
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.project.domain.repositories.sprint_repository import SprintRepository
from app.context.project.domain.value_objects.sprint_goal import SprintGoal
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)


class CreateSprintCommand(BaseCommand):
    """
    Команда создания спринта.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        project_id: ID проекта.
        name: Название спринта.
        goal: Цель спринта.
        start_date: Дата начала (ISO).
        end_date: Дата окончания (ISO).
    """

    caller_id: str
    project_id: str
    name: str
    goal: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class CreateSprintHandler(BaseCommandHandler[CreateSprintCommand, SprintDTO]):
    """
    Обработчик создания спринта.

    Проверяет capabilities.has_sprints.
    """


    REQUIRED_PERMISSION = "sprints.write"

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
    async def handle(self, command: CreateSprintCommand) -> SprintDTO:
        project_id = Id.from_string(command.project_id)
        project = await self._project_repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundException(command.project_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=project_id,
            permission=self.REQUIRED_PERMISSION,
        )

        if not project.methodology_capabilities.has_sprints:
            raise SprintCapabilityNotAvailableException(project.methodology.value)

        goal = SprintGoal(value=command.goal) if command.goal else None
        date_range: DateRange | None = None
        if command.start_date and command.end_date:
            date_range = DateRange(
                start=date.fromisoformat(command.start_date),
                end=date.fromisoformat(command.end_date),
            )

        sprint = Sprint.create(
            name=command.name,
            project_id=Id.from_string(command.project_id),
            goal=goal,
            date_range=date_range,
        )
        await self._sprint_repo.add(sprint)
        await self._event_bus.publish_all(sprint.clear_domain_events())

        return SprintDTO(
            id=str(sprint.id),
            project_id=str(sprint.project_id),
            name=sprint.name,
            goal=sprint.goal.value if sprint.goal else None,
            status=sprint.status.value,
            date_range={"start": str(date_range.start), "end": str(date_range.end)} if date_range else None,
            created_at=sprint.created_at,
            updated_at=sprint.updated_at,
        )
