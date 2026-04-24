from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.exceptions.invitation_exceptions import InvitationNotFoundException
from app.context.organization.domain.repositories.invitation_repository import InvitationRepository


class DeclineInvitationCommand(BaseCommand):
    """
    Команда отклонения приглашения.

    Атрибуты:
        invitation_id: ID приглашения.
    """

    invitation_id: str


class DeclineInvitationHandler(BaseCommandHandler[DeclineInvitationCommand, None]):
    """
    Обработчик отклонения приглашения.

    Загружает Invitation, вызывает decline, сохраняет.
    """

    def __init__(
        self,
        invitation_repo: InvitationRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._invitation_repo = invitation_repo
        self._event_bus = event_bus

    async def handle(self, command: DeclineInvitationCommand) -> None:
        invitation = await self._invitation_repo.get_by_id(Id.from_string(command.invitation_id))
        if invitation is None:
            raise InvitationNotFoundException(command.invitation_id)

        invitation.decline()
        await self._invitation_repo.update(invitation)
        await self._event_bus.publish_all(invitation.clear_domain_events())
