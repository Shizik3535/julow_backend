from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.exceptions.workspace_invitation_exceptions import InvitationNotFoundException
from app.context.workspace.domain.repositories.workspace_invitation_repository import WorkspaceInvitationRepository


class DeclineWorkspaceInvitationCommand(BaseCommand):
    """
    Команда отклонения приглашения в workspace.

    Атрибуты:
        invitation_id: ID приглашения.
    """

    invitation_id: str


class DeclineWorkspaceInvitationHandler(BaseCommandHandler[DeclineWorkspaceInvitationCommand, None]):
    """Обработчик отклонения приглашения."""

    def __init__(
        self,
        invitation_repo: WorkspaceInvitationRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._invitation_repo = invitation_repo
        self._event_bus = event_bus

    async def handle(self, command: DeclineWorkspaceInvitationCommand) -> None:
        invitation = await self._invitation_repo.get_by_id(Id.from_string(command.invitation_id))
        if invitation is None:
            raise InvitationNotFoundException(command.invitation_id)

        invitation.decline()
        await self._invitation_repo.update(invitation)
        await self._event_bus.publish_all(invitation.clear_domain_events())
