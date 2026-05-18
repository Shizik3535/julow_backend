from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.exceptions.membership_app_exceptions import (
    MemberAlreadyExistsException,
    UserNotFoundException,
)
from app.context.project.application.ports.integration.inboard.identity_user_port import IdentityUserPort
from app.context.project.application.ports.integration.inboard.workspace_membership_port import (
    WorkspaceMembershipPort,
)
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from app.context.project.domain.exceptions.project_invitation_exceptions import (
    ProjectInvitationNotFoundException,
)
from app.context.project.domain.repositories.project_invitation_repository import (
    ProjectInvitationRepository,
)
from app.context.project.domain.repositories.project_membership_repository import (
    ProjectMembershipRepository,
)
from app.context.project.domain.value_objects.membership_type import MembershipType


class AcceptProjectInvitationCommand(BaseCommand):
    """
    Команда принятия приглашения в проект.

    Поддерживает два сценария входа:
    - По invitation_id (после получения приглашения через UI).
    - По token (вход по коду/ссылке).

    Хотя бы один из двух должен быть указан.

    Атрибуты:
        invitation_id: ID приглашения (опционально).
        token: Значение токена ссылки/кода (опционально).
        user_id: ID пользователя, принимающего приглашение.
    """

    invitation_id: str | None = None
    token: str | None = None
    user_id: str


class AcceptProjectInvitationHandler(BaseCommandHandler[AcceptProjectInvitationCommand, dict]):
    """
    Обработчик принятия приглашения в проект.

    Мульти-AR:
        - invitation.accept() + increment_link_usage()
        - membership.add_member()

    Если пользователь не является участником workspace, добавляется как GUEST.
    """

    def __init__(
        self,
        invitation_repo: ProjectInvitationRepository,
        membership_repo: ProjectMembershipRepository,
        identity_port: IdentityUserPort,
        workspace_membership_port: WorkspaceMembershipPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._invitation_repo = invitation_repo
        self._membership_repo = membership_repo
        self._identity_port = identity_port
        self._workspace_membership_port = workspace_membership_port
        self._event_bus = event_bus

    async def handle(self, command: AcceptProjectInvitationCommand) -> dict:
        if not await self._identity_port.user_exists(command.user_id):
            raise UserNotFoundException(command.user_id)

        invitation = None
        if command.invitation_id:
            invitation = await self._invitation_repo.get_by_id(
                Id.from_string(command.invitation_id)
            )
        elif command.token:
            invitation = await self._invitation_repo.get_by_token(command.token)

        if invitation is None:
            raise ProjectInvitationNotFoundException(
                command.invitation_id or command.token or "unknown"
            )

        user_id = Id.from_string(command.user_id)
        invitation.accept(user_id=user_id)

        if invitation.link is not None:
            invitation.increment_link_usage()

        membership = await self._membership_repo.get_by_project_id(invitation.project_id)
        if membership is None:
            raise ProjectNotFoundException(str(invitation.project_id))

        existing = membership._find_member(user_id)
        if existing is not None:
            raise MemberAlreadyExistsException(command.user_id, str(invitation.project_id))

        # Определяем тип членства: STANDARD если пользователь в workspace, GUEST иначе.
        is_ws_member = await self._workspace_membership_port.is_workspace_member(
            str(invitation.workspace_id), command.user_id
        )
        membership_type = MembershipType.STANDARD if is_ws_member else MembershipType.GUEST

        membership.add_member(
            user_id=user_id,
            role_id=invitation.role_id,
            invited_by=invitation.invited_by,
            membership_type=membership_type,
        )

        await self._invitation_repo.update(invitation)
        await self._membership_repo.update(membership)
        await self._event_bus.publish_all(invitation.clear_domain_events())
        await self._event_bus.publish_all(membership.clear_domain_events())

        return {
            "project_id": str(invitation.project_id),
            "workspace_id": str(invitation.workspace_id),
            "role_id": str(invitation.role_id),
            "membership_type": membership_type.value,
        }
