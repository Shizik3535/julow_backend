from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.exceptions.authorization_exceptions import (
    InsufficientWorkspacePermissionsException,
)
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.exceptions.workspace_role_exceptions import WorkspaceRoleNotFoundException
from app.context.workspace.domain.repositories.workspace_role_repository import WorkspaceRoleRepository


class UpdateWorkspaceRoleCommand(BaseCommand):
    """
    Команда обновления роли workspace.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        role_id: ID роли.
        permissions: Новый список разрешений.
        description: Новое описание.
    """

    caller_id: str
    role_id: str
    permissions: list[str] | None = None
    description: str | None = None


class UpdateWorkspaceRoleHandler(BaseCommandHandler[UpdateWorkspaceRoleCommand, None]):
    """Обработчик обновления роли workspace."""

    REQUIRED_PERMISSION = "roles.write"

    def __init__(
        self,
        role_repo: WorkspaceRoleRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._role_repo = role_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: UpdateWorkspaceRoleCommand) -> None:
        role = await self._role_repo.get_by_id(Id.from_string(command.role_id))
        if role is None:
            raise WorkspaceRoleNotFoundException(command.role_id)

        # Системные роли (workspace_id=None) недоступны для привилегированного изменения
        # на уровне workspace: такие роли управляются системными сеидами.
        if role.workspace_id is None:
            raise InsufficientWorkspacePermissionsException(
                permission=self.REQUIRED_PERMISSION, workspace_id=""
            )

        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            workspace_id=role.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )

        role.update(permissions=command.permissions, description=command.description)
        await self._role_repo.update(role)
        await self._event_bus.publish_all(role.clear_domain_events())
