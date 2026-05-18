from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.project_invitation_dto import ProjectInvitationDTO
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)
from app.context.project.domain.aggregates.project_invitation import ProjectInvitation
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from app.context.project.domain.repositories.project_invitation_repository import (
    ProjectInvitationRepository,
)
from app.context.project.domain.repositories.project_repository import ProjectRepository


class GenerateProjectInvitationLinkCommand(BaseCommand):
    """
    Команда генерации ссылки/кода приглашения в проект.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        project_id: ID проекта.
        role_id: ID роли проекта.
        expires_at: Время истечения (ISO string) или None.
        max_uses: Максимум использований или None.
    """

    caller_id: str
    project_id: str
    role_id: str
    expires_at: str | None = None
    max_uses: int | None = None


class GenerateProjectInvitationLinkHandler(
    BaseCommandHandler[GenerateProjectInvitationLinkCommand, ProjectInvitationDTO]
):
    """Обработчик генерации ссылки/кода приглашения в проект."""

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

    async def handle(self, command: GenerateProjectInvitationLinkCommand) -> ProjectInvitationDTO:
        project_id = Id.from_string(command.project_id)

        project = await self._project_repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundException(command.project_id)

        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=project_id,
            permission=self.REQUIRED_PERMISSION,
        )

        token_value = uuid4().hex  # 32 hex chars, можно усечь для UI до 8 как «короткий код»
        expires_at = datetime.fromisoformat(command.expires_at) if command.expires_at else None

        invitation = ProjectInvitation.create_link_invitation(
            project_id=project_id,
            workspace_id=project.workspace_id or Id.generate(),
            role_id=Id.from_string(command.role_id),
            invited_by=Id.from_string(command.caller_id),
            token_value=token_value,
            expires_at=expires_at,
            max_uses=command.max_uses,
        )

        await self._invitation_repo.add(invitation)
        await self._event_bus.publish_all(invitation.clear_domain_events())

        return ProjectInvitationDTO(
            id=str(invitation.id),
            project_id=str(invitation.project_id),
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
            project_name=project.name,
            created_at=invitation.created_at,
            updated_at=invitation.updated_at,
        )
