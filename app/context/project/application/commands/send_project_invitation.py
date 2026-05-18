from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.project_invitation_dto import ProjectInvitationDTO
from app.context.project.application.exceptions.invitation_app_exceptions import (
    DuplicateInvitationForEmailException,
)
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)
from app.context.project.domain.aggregates.project_invitation import ProjectInvitation
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from app.context.project.domain.repositories.project_invitation_repository import (
    ProjectInvitationRepository,
)
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.project.domain.value_objects.invitation_status import InvitationStatus


class SendProjectInvitationCommand(BaseCommand):
    """
    Команда отправки email-приглашения в проект.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        project_id: ID проекта.
        email: Email приглашаемого.
        role_id: ID роли проекта.
    """

    caller_id: str
    project_id: str
    email: str
    role_id: str


class SendProjectInvitationHandler(BaseCommandHandler[SendProjectInvitationCommand, ProjectInvitationDTO]):
    """Обработчик отправки email-приглашения в проект."""

    REQUIRED_PERMISSION = "members.write"

    def __init__(
        self,
        invitation_repo: ProjectInvitationRepository,
        project_repo: ProjectRepository,
        permission_checker: ProjectPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._invitation_repo = invitation_repo
        self._project_repo = project_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: SendProjectInvitationCommand) -> ProjectInvitationDTO:
        project_id = Id.from_string(command.project_id)

        project = await self._project_repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundException(command.project_id)

        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=project_id,
            permission=self.REQUIRED_PERMISSION,
        )

        pending = await self._invitation_repo.get_pending_by_project(project_id)
        for inv in pending:
            if (
                inv.email is not None
                and str(inv.email) == command.email
                and inv.status == InvitationStatus.PENDING
            ):
                raise DuplicateInvitationForEmailException(command.email, command.project_id)

        invitation = ProjectInvitation.create_email_invitation(
            project_id=project_id,
            workspace_id=project.workspace_id or Id.generate(),
            email=Email(command.email),
            role_id=Id.from_string(command.role_id),
            invited_by=Id.from_string(command.caller_id),
        )

        await self._invitation_repo.add(invitation)
        await self._event_bus.publish_all(invitation.clear_domain_events())

        return ProjectInvitationDTO(
            id=str(invitation.id),
            project_id=str(invitation.project_id),
            workspace_id=str(invitation.workspace_id),
            email=str(invitation.email) if invitation.email else None,
            link=None,
            role_id=str(invitation.role_id),
            invited_by=str(invitation.invited_by),
            invited_at=invitation.invited_at,
            status=invitation.status.value,
            project_name=project.name,
            created_at=invitation.created_at,
            updated_at=invitation.updated_at,
        )
