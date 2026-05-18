from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.exceptions.membership_app_exceptions import UserNotFoundException
from app.context.project.application.ports.integration.inboard.identity_user_port import IdentityUserPort
from app.context.project.domain.exceptions.project_invitation_exceptions import (
    ProjectInvitationNotFoundException,
)
from app.context.project.domain.repositories.project_invitation_repository import (
    ProjectInvitationRepository,
)


class DeclineProjectInvitationCommand(BaseCommand):
    """
    Команда отклонения приглашения в проект.

    Атрибуты:
        invitation_id: ID приглашения.
        user_id: ID пользователя, отклоняющего приглашение.
    """

    invitation_id: str
    user_id: str


class DeclineProjectInvitationHandler(BaseCommandHandler[DeclineProjectInvitationCommand, None]):
    """Обработчик отклонения приглашения в проект."""

    def __init__(
        self,
        invitation_repo: ProjectInvitationRepository,
        identity_port: IdentityUserPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._invitation_repo = invitation_repo
        self._identity_port = identity_port
        self._event_bus = event_bus

    async def handle(self, command: DeclineProjectInvitationCommand) -> None:
        if not await self._identity_port.user_exists(command.user_id):
            raise UserNotFoundException(command.user_id)

        invitation = await self._invitation_repo.get_by_id(Id.from_string(command.invitation_id))
        if invitation is None:
            raise ProjectInvitationNotFoundException(command.invitation_id)

        invitation.decline(user_id=Id.from_string(command.user_id))
        await self._invitation_repo.update(invitation)
        await self._event_bus.publish_all(invitation.clear_domain_events())
