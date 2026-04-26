from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.dto.workspace_dto import WorkspaceDTO
from app.context.workspace.application.exceptions.authorization_exceptions import (
    InsufficientWorkspacePermissionsException,
)
from app.context.workspace.application.exceptions.membership_app_exceptions import UserNotFoundException
from app.context.workspace.application.ports.integration.inboard.identity_user_port import IdentityUserPort
from app.context.workspace.application.ports.integration.inboard.organization_permission_checker_port import (
    OrganizationPermissionCheckerPort,
)
from app.context.workspace.domain.aggregates.workspace import Workspace
from app.context.workspace.domain.aggregates.workspace_membership import WorkspaceMembership
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository
from app.context.workspace.domain.repositories.workspace_membership_repository import WorkspaceMembershipRepository
from app.context.workspace.domain.repositories.workspace_role_repository import WorkspaceRoleRepository
from app.context.workspace.domain.value_objects.workspace_type import WorkspaceType


class CreateWorkspaceCommand(BaseCommand):
    """
    Команда создания workspace.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        name: Название workspace.
        owner_id: ID владельца.
        workspace_type: Тип workspace (PERSONAL, TEAM, ENTERPRISE).
        organization_id: ID организации (None — независимый).
        parent_workspace_id: ID родительского workspace (None — корневой).
    """

    caller_id: str
    name: str
    owner_id: str
    workspace_type: str = "TEAM"
    organization_id: str | None = None
    parent_workspace_id: str | None = None


class CreateWorkspaceHandler(BaseCommandHandler[CreateWorkspaceCommand, WorkspaceDTO]):
    """
    Обработчик создания workspace.

    Мульти-AR: создаёт Workspace + WorkspaceMembership с владельцем.

    Кросс-BC авторизация: если указан organization_id, проверяется
    орг-разрешение «workspaces.create» через OrganizationPermissionCheckerPort.
    Для независимого workspace (без organization_id) проверка не требуется.
    """

    REQUIRED_ORG_PERMISSION = "workspaces.create"

    def __init__(
        self,
        ws_repo: WorkspaceRepository,
        membership_repo: WorkspaceMembershipRepository,
        role_repo: WorkspaceRoleRepository,
        identity_port: IdentityUserPort,
        org_permission_checker: OrganizationPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._ws_repo = ws_repo
        self._membership_repo = membership_repo
        self._role_repo = role_repo
        self._identity_port = identity_port
        self._org_permission_checker = org_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: CreateWorkspaceCommand) -> WorkspaceDTO:
        # Кросс-BC проверка: если workspace создаётся в рамках организации,
        # caller должен обладать орг-разрешением «workspaces.create».
        if command.organization_id is not None:
            has_perm = await self._org_permission_checker.has_permission(
                user_id=command.caller_id,
                org_id=command.organization_id,
                permission=self.REQUIRED_ORG_PERMISSION,
            )
            if not has_perm:
                raise InsufficientWorkspacePermissionsException(
                    permission=self.REQUIRED_ORG_PERMISSION,
                    workspace_id=command.organization_id,
                )

        if not await self._identity_port.user_exists(command.owner_id):
            raise UserNotFoundException(command.owner_id)

        owner_id = Id.from_string(command.owner_id)

        # Проверка существования родительского workspace, если указан.
        if command.parent_workspace_id is not None:
            parent_id = Id.from_string(command.parent_workspace_id)
            parent = await self._ws_repo.get_by_id(parent_id)
            if parent is None:
                raise WorkspaceNotFoundException(command.parent_workspace_id)

        try:
            ws_type = WorkspaceType(command.workspace_type)
        except ValueError:
            ws_type = WorkspaceType[command.workspace_type]

        workspace = Workspace.create(
            name=command.name,
            owner_id=owner_id,
            workspace_type=ws_type,
            organization_id=Id.from_string(command.organization_id) if command.organization_id else None,
            parent_workspace_id=Id.from_string(command.parent_workspace_id) if command.parent_workspace_id else None,
        )

        owner_role = await self._role_repo.get_by_name("owner")
        if owner_role is None:
            raise ValueError("System role 'owner' not found")

        membership = WorkspaceMembership.create(
            workspace_id=workspace.id,
            owner_id=owner_id,
            owner_role_id=owner_role.id,
        )

        await self._ws_repo.add(workspace)
        await self._membership_repo.add(membership)
        await self._event_bus.publish_all(workspace.clear_domain_events())
        await self._event_bus.publish_all(membership.clear_domain_events())

        return WorkspaceDTO(
            id=str(workspace.id),
            name=workspace.name,
            status=workspace.status.value,
            workspace_type=workspace.workspace_type.value,
            organization_id=str(workspace.organization_id) if workspace.organization_id else None,
            parent_workspace_id=str(workspace.parent_workspace_id) if workspace.parent_workspace_id else None,
            owner_ids=[str(oid) for oid in workspace.owner_ids],
            created_at=workspace.created_at,
            updated_at=workspace.updated_at,
        )
