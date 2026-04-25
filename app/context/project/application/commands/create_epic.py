from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.epic_dto import EpicDTO
from app.context.project.application.exceptions.sprint_app_exceptions import EpicCapabilityNotAvailableException
from app.context.project.domain.aggregates.epic import Epic
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from app.context.project.domain.repositories.epic_repository import EpicRepository
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)


class CreateEpicCommand(BaseCommand):
    """
    Команда создания эпика.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        project_id: ID проекта.
        name: Название эпика.
        owner_id: ID владельца эпика.
    """

    caller_id: str
    project_id: str
    name: str
    owner_id: str | None = None


class CreateEpicHandler(BaseCommandHandler[CreateEpicCommand, EpicDTO]):
    """
    Обработчик создания эпика.

    Проверяет capabilities.has_epics.
    """


    REQUIRED_PERMISSION = "epics.write"

    def __init__(
        self,
        project_repo: ProjectRepository,
        epic_repo: EpicRepository,
        permission_checker: ProjectPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._project_repo = project_repo
        self._epic_repo = epic_repo
        self._event_bus = event_bus
        self._permission_checker = permission_checker
    async def handle(self, command: CreateEpicCommand) -> EpicDTO:
        project_id = Id.from_string(command.project_id)
        project = await self._project_repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundException(command.project_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=project_id,
            permission=self.REQUIRED_PERMISSION,
        )

        if not project.methodology_capabilities.has_epics:
            raise EpicCapabilityNotAvailableException(project.methodology.value)

        owner_id = Id.from_string(command.owner_id) if command.owner_id else None
        epic = Epic.create(
            project_id=Id.from_string(command.project_id),
            name=command.name,
            owner_id=owner_id,
        )
        await self._epic_repo.add(epic)
        await self._event_bus.publish_all(epic.clear_domain_events())

        return EpicDTO(
            id=str(epic.id),
            project_id=str(epic.project_id),
            name=epic.name,
            status=epic.status.value,
            owner_id=str(epic.owner_id) if epic.owner_id else None,
            created_at=epic.created_at,
            updated_at=epic.updated_at,
        )
