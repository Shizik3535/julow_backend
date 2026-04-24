from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.exceptions.membership_app_exceptions import (
    MemberAlreadyExistsException,
    UserNotFoundException,
)
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.application.ports.integration.inboard.identity_user_port import IdentityUserPort
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from app.context.workspace.domain.repositories.workspace_membership_repository import WorkspaceMembershipRepository
from app.context.workspace.domain.value_objects.member_source import MemberSource


class AddWorkspaceMemberCommand(BaseCommand):
    """
    Команда добавления участника в workspace.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        workspace_id: ID workspace.
        user_id: ID пользователя.
        role_id: ID роли.
        source: Источник (DIRECT, ORGANIZATION, PARENT_WORKSPACE, INVITATION_LINK).
        invited_by: ID пригласившего.
        display_name: Отображаемое имя.
    """

    caller_id: str
    workspace_id: str
    user_id: str
    role_id: str
    source: str = "DIRECT"
    invited_by: str | None = None
    display_name: str | None = None


class AddWorkspaceMemberHandler(BaseCommandHandler[AddWorkspaceMemberCommand, None]):
    """Обработчик добавления участника в workspace."""

    REQUIRED_PERMISSION = "members.write"

    def __init__(
        self,
        membership_repo: WorkspaceMembershipRepository,
        identity_port: IdentityUserPort,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._membership_repo = membership_repo
        self._identity_port = identity_port
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: AddWorkspaceMemberCommand) -> None:
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            workspace_id=Id.from_string(command.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )

        if not await self._identity_port.user_exists(command.user_id):
            raise UserNotFoundException(command.user_id)

        ws_id = Id.from_string(command.workspace_id)
        membership = await self._membership_repo.get_by_workspace_id(ws_id)
        if membership is None:
            raise WorkspaceNotFoundException(command.workspace_id)

        user_id = Id.from_string(command.user_id)
        existing = membership._find_member(user_id)
        if existing is not None:
            raise MemberAlreadyExistsException(command.user_id, command.workspace_id)

        membership.add_member(
            user_id=user_id,
            role_id=Id.from_string(command.role_id),
            source=MemberSource(command.source),
            invited_by=Id.from_string(command.invited_by) if command.invited_by else None,
            display_name=command.display_name,
        )

        await self._membership_repo.update(membership)
        await self._event_bus.publish_all(membership.clear_domain_events())
