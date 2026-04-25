from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.dto.workspace_invitation_dto import WorkspaceInvitationDTO
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.aggregates.workspace_invitation import WorkspaceInvitation
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from app.context.workspace.domain.repositories.workspace_invitation_repository import WorkspaceInvitationRepository
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository


class GenerateWorkspaceInvitationLinkCommand(BaseCommand):
    """
    Команда генерации ссылки-приглашения в workspace.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        workspace_id: ID workspace.
        role_id: ID роли.
        invited_by: ID пригласившего.
        expires_at: Время истечения (ISO string) или None.
        max_uses: Максимум использований или None.
    """

    caller_id: str
    workspace_id: str
    role_id: str
    invited_by: str
    expires_at: str | None = None
    max_uses: int | None = None


class GenerateWorkspaceInvitationLinkHandler(
    BaseCommandHandler[GenerateWorkspaceInvitationLinkCommand, WorkspaceInvitationDTO]
):
    """Обработчик генерации ссылки-приглашения."""

    REQUIRED_PERMISSION = "members.invite"

    def __init__(
        self,
        invitation_repo: WorkspaceInvitationRepository,
        ws_repo: WorkspaceRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._invitation_repo = invitation_repo
        self._ws_repo = ws_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: GenerateWorkspaceInvitationLinkCommand) -> WorkspaceInvitationDTO:
        ws_id = Id.from_string(command.workspace_id)

        ws = await self._ws_repo.get_by_id(ws_id)
        if ws is None:
            raise WorkspaceNotFoundException(command.workspace_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            workspace_id=ws_id,
            permission=self.REQUIRED_PERMISSION,
        )
        token_value = str(uuid4())
        expires_at = datetime.fromisoformat(command.expires_at) if command.expires_at else None

        invitation = WorkspaceInvitation.create_link_invitation(
            workspace_id=Id.from_string(command.workspace_id),
            role_id=Id.from_string(command.role_id),
            invited_by=Id.from_string(command.invited_by),
            token_value=token_value,
            expires_at=expires_at,
            max_uses=command.max_uses,
        )

        await self._invitation_repo.add(invitation)
        await self._event_bus.publish_all(invitation.clear_domain_events())

        return WorkspaceInvitationDTO(
            id=str(invitation.id),
            workspace_id=str(invitation.workspace_id),
            email=None,
            link={
                "value": invitation.link.value,
                "expires_at": invitation.link.expires_at.isoformat() if invitation.link.expires_at else None,
                "max_uses": invitation.link.max_uses,
                "used_count": invitation.link.used_count,
            } if invitation.link else None,
            role_id=str(invitation.role_id),
            invited_by=str(invitation.invited_by),
            invited_at=invitation.invited_at,
            status=invitation.status.value,
            created_at=invitation.created_at,
            updated_at=invitation.updated_at,
        )
