from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)
from app.context.project.domain.exceptions.project_invitation_exceptions import (
    ProjectInvitationNotFoundException,
)
from app.context.project.domain.repositories.project_invitation_repository import (
    ProjectInvitationRepository,
)


class RevokeProjectInvitationCommand(BaseCommand):
    """
    Команда отзыва приглашения в проект.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        project_id: ID проекта.
        invitation_id: ID приглашения.
    """

    caller_id: str
    project_id: str
    invitation_id: str


class RevokeProjectInvitationHandler(BaseCommandHandler[RevokeProjectInvitationCommand, None]):
    """Обработчик отзыва приглашения в проект."""

    REQUIRED_PERMISSION = "members.write"

    def __init__(
        self,
        invitation_repo: ProjectInvitationRepository,
        permission_checker: ProjectPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._invitation_repo = invitation_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: RevokeProjectInvitationCommand) -> None:
        project_id = Id.from_string(command.project_id)

        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=project_id,
            permission=self.REQUIRED_PERMISSION,
        )

        invitation = await self._invitation_repo.get_by_id(Id.from_string(command.invitation_id))
        if invitation is None:
            raise ProjectInvitationNotFoundException(command.invitation_id)

        invitation.revoke()
        await self._invitation_repo.update(invitation)
        await self._event_bus.publish_all(invitation.clear_domain_events())
