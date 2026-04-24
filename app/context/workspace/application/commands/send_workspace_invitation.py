from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.dto.workspace_invitation_dto import WorkspaceInvitationDTO
from app.context.workspace.application.exceptions.invitation_app_exceptions import DuplicateInvitationForEmailException
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.aggregates.workspace_invitation import WorkspaceInvitation
from app.context.workspace.domain.repositories.workspace_invitation_repository import WorkspaceInvitationRepository
from app.context.workspace.domain.value_objects.invitation_status import InvitationStatus


class SendWorkspaceInvitationCommand(BaseCommand):
    """
    Команда отправки email-приглашения в workspace.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        workspace_id: ID workspace.
        email: Email приглашаемого.
        role_id: ID роли.
        invited_by: ID пригласившего.
    """

    caller_id: str
    workspace_id: str
    email: str
    role_id: str
    invited_by: str


class SendWorkspaceInvitationHandler(BaseCommandHandler[SendWorkspaceInvitationCommand, WorkspaceInvitationDTO]):
    """Обработчик отправки email-приглашения в workspace."""

    REQUIRED_PERMISSION = "members.invite"

    def __init__(
        self,
        invitation_repo: WorkspaceInvitationRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._invitation_repo = invitation_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: SendWorkspaceInvitationCommand) -> WorkspaceInvitationDTO:
        ws_id = Id.from_string(command.workspace_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            workspace_id=ws_id,
            permission=self.REQUIRED_PERMISSION,
        )
        pending = await self._invitation_repo.get_pending_by_workspace(ws_id)
        for inv in pending:
            if inv.email is not None and str(inv.email) == command.email and inv.status == InvitationStatus.PENDING:
                raise DuplicateInvitationForEmailException(command.email, command.workspace_id)

        invitation = WorkspaceInvitation.create_email_invitation(
            workspace_id=ws_id,
            email=Email(command.email),
            role_id=Id.from_string(command.role_id),
            invited_by=Id.from_string(command.invited_by),
        )

        await self._invitation_repo.add(invitation)
        await self._event_bus.publish_all(invitation.clear_domain_events())

        return WorkspaceInvitationDTO(
            id=str(invitation.id),
            workspace_id=str(invitation.workspace_id),
            email=str(invitation.email) if invitation.email else None,
            link=None,
            role_id=str(invitation.role_id),
            invited_by=str(invitation.invited_by),
            invited_at=invitation.invited_at,
            status=invitation.status.value,
            created_at=invitation.created_at,
            updated_at=invitation.updated_at,
        )
