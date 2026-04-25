from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.project_role_dto import ProjectRoleDTO
from app.context.project.domain.aggregates.project_role import ProjectRole
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.project.domain.repositories.project_role_repository import ProjectRoleRepository
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)


class CreateProjectRoleCommand(BaseCommand):
    """
    Команда создания кастомной роли проекта.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        project_id: ID проекта.
        name: Название роли.
        permissions: Список разрешений.
        description: Описание.
    """

    caller_id: str
    project_id: str
    name: str
    permissions: list[str]
    description: str | None = None


class CreateProjectRoleHandler(BaseCommandHandler[CreateProjectRoleCommand, ProjectRoleDTO]):
    """Обработчик создания кастомной роли проекта."""


    REQUIRED_PERMISSION = "roles.*"

    def __init__(self, project_repo: ProjectRepository, role_repo: ProjectRoleRepository, permission_checker: ProjectPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._project_repo = project_repo
        self._role_repo = role_repo
        self._event_bus = event_bus
        self._permission_checker = permission_checker

    async def handle(self, command: CreateProjectRoleCommand) -> ProjectRoleDTO:
        project_id = Id.from_string(command.project_id)
        project = await self._project_repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundException(command.project_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=project_id,
            permission=self.REQUIRED_PERMISSION,
        )
        role = ProjectRole.create_custom(
            project_id=Id.from_string(command.project_id),
            name=command.name,
            permissions=command.permissions,
            description=command.description,
        )
        await self._role_repo.add(role)
        await self._event_bus.publish_all(role.clear_domain_events())

        return ProjectRoleDTO(
            id=str(role.id),
            project_id=str(role.project_id) if role.project_id else "",
            name=role.name,
            permissions=role.permissions,
            is_system=role.is_system,
            description=role.description,
            created_at=role.created_at,
            updated_at=role.updated_at,
        )
