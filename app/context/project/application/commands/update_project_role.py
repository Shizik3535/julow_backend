from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.exceptions.project_role_exceptions import ProjectRoleNotFoundException
from app.context.project.domain.repositories.project_role_repository import ProjectRoleRepository
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)


class UpdateProjectRoleCommand(BaseCommand):
    """
    Команда обновления роли проекта.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        project_id: ID проекта.
        role_id: ID роли.
        permissions: Новые разрешения.
        description: Описание.
    """

    caller_id: str
    project_id: str
    role_id: str
    permissions: list[str] | None = None
    description: str | None = None


class UpdateProjectRoleHandler(BaseCommandHandler[UpdateProjectRoleCommand, None]):
    """Обработчик обновления роли проекта."""


    REQUIRED_PERMISSION = "roles.*"

    def __init__(self, role_repo: ProjectRoleRepository, permission_checker: ProjectPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._role_repo = role_repo
        self._event_bus = event_bus
        self._permission_checker = permission_checker

    async def handle(self, command: UpdateProjectRoleCommand) -> None:
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=Id.from_string(command.project_id),
            permission=self.REQUIRED_PERMISSION,
        )
        role = await self._role_repo.get_by_id(Id.from_string(command.role_id))
        if role is None:
            raise ProjectRoleNotFoundException(command.role_id)

        role.update(permissions=command.permissions, description=command.description)
        await self._role_repo.update(role)
        await self._event_bus.publish_all(role.clear_domain_events())
