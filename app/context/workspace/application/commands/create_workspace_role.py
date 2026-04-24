from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.dto.workspace_role_dto import WorkspaceRoleDTO
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.aggregates.workspace_role import WorkspaceRole
from app.context.workspace.domain.repositories.workspace_role_repository import WorkspaceRoleRepository


class CreateWorkspaceRoleCommand(BaseCommand):
    """
    Команда создания кастомной роли workspace.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        workspace_id: ID workspace.
        name: Название роли.
        permissions: Список разрешений.
        description: Описание.
    """

    caller_id: str
    workspace_id: str
    name: str
    permissions: list[str]
    description: str | None = None


class CreateWorkspaceRoleHandler(BaseCommandHandler[CreateWorkspaceRoleCommand, WorkspaceRoleDTO]):
    """Обработчик создания кастомной роли workspace."""

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

    async def handle(self, command: CreateWorkspaceRoleCommand) -> WorkspaceRoleDTO:
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            workspace_id=Id.from_string(command.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )
        role = WorkspaceRole.create_custom(
            workspace_id=Id.from_string(command.workspace_id),
            name=command.name,
            permissions=command.permissions,
            description=command.description,
        )

        await self._role_repo.add(role)
        await self._event_bus.publish_all(role.clear_domain_events())

        return WorkspaceRoleDTO(
            id=str(role.id),
            workspace_id=str(role.workspace_id) if role.workspace_id else "",
            name=role.name,
            permissions=role.permissions,
            is_system=role.is_system,
            description=role.description,
            created_at=role.created_at,
            updated_at=role.updated_at,
        )
