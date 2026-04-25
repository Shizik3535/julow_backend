from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.exceptions.membership_app_exceptions import (
    MemberAlreadyExistsException,
    MemberNotInWorkspaceException,
    UserNotFoundException,
)
from app.context.project.application.ports.integration.inboard.identity_user_port import IdentityUserPort
from app.context.project.application.ports.integration.inboard.workspace_membership_port import WorkspaceMembershipPort
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from app.context.project.domain.repositories.project_membership_repository import ProjectMembershipRepository
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)


class AddProjectMemberCommand(BaseCommand):
    """
    Команда добавления участника в проект.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        project_id: ID проекта.
        user_id: ID пользователя.
        role_id: ID роли.
        invited_by: ID пригласившего.
    """

    caller_id: str
    project_id: str
    user_id: str
    role_id: str
    invited_by: str | None = None


class AddProjectMemberHandler(BaseCommandHandler[AddProjectMemberCommand, None]):
    """
    Обработчик добавления участника в проект.

    ACL: проверка существования пользователя + членство в workspace.
    """


    REQUIRED_PERMISSION = "members.write"

    def __init__(
        self,
        project_repo: ProjectRepository,
        membership_repo: ProjectMembershipRepository,
        identity_port: IdentityUserPort,
        workspace_membership_port: WorkspaceMembershipPort,
        permission_checker: ProjectPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._project_repo = project_repo
        self._membership_repo = membership_repo
        self._identity_port = identity_port
        self._workspace_membership_port = workspace_membership_port
        self._event_bus = event_bus
        self._permission_checker = permission_checker
    async def handle(self, command: AddProjectMemberCommand) -> None:
        if not await self._identity_port.user_exists(command.user_id):
            raise UserNotFoundException(command.user_id)

        project_id = Id.from_string(command.project_id)
        project = await self._project_repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundException(command.project_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=project_id,
            permission=self.REQUIRED_PERMISSION,
        )

        workspace_id = str(project.workspace_id) if project.workspace_id else ""
        if workspace_id and not await self._workspace_membership_port.is_workspace_member(workspace_id, command.user_id):
            raise MemberNotInWorkspaceException(command.user_id, workspace_id)

        membership = await self._membership_repo.get_by_project_id(Id.from_string(command.project_id))
        if membership is None:
            raise ProjectNotFoundException(command.project_id)

        existing = membership._find_member(Id.from_string(command.user_id))
        if existing is not None:
            raise MemberAlreadyExistsException(command.user_id, command.project_id)

        membership.add_member(
            user_id=Id.from_string(command.user_id),
            role_id=Id.from_string(command.role_id),
            invited_by=Id.from_string(command.invited_by) if command.invited_by else None,
        )
        await self._membership_repo.update(membership)
        await self._event_bus.publish_all(membership.clear_domain_events())
