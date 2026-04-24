from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.project_dto import ProjectDTO
from app.context.project.application.exceptions.authorization_exceptions import (
    InsufficientProjectPermissionsException,
)
from app.context.project.application.exceptions.membership_app_exceptions import UserNotFoundException
from app.context.project.application.ports.integration.inboard.identity_user_port import IdentityUserPort
from app.context.project.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.project.application.ports.integration.inboard.workspace_port import WorkspacePort
from app.context.project.domain.aggregates.board import Board
from app.context.project.domain.aggregates.project import Project
from app.context.project.domain.aggregates.project_membership import ProjectMembership
from app.context.project.domain.repositories.board_repository import BoardRepository
from app.context.project.domain.repositories.project_membership_repository import ProjectMembershipRepository
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.project.domain.repositories.project_role_repository import ProjectRoleRepository
from app.context.project.domain.value_objects.methodology import Methodology
from app.context.project.infrastructure.persistence.seed.system_project_roles import (
    build_system_project_roles,
)


class CreateProjectCommand(BaseCommand):
    """
    Команда создания проекта.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        name: Название проекта.
        workspace_id: ID workspace.
        owner_id: ID владельца.
        methodology: Методология (KANBAN, SCRUM, WATERFALL, HYBRID, SHAPE_UP).
    """

    caller_id: str
    name: str
    workspace_id: str
    owner_id: str
    methodology: str = "KANBAN"


class CreateProjectHandler(BaseCommandHandler[CreateProjectCommand, ProjectDTO]):
    """
    Обработчик создания проекта.

    Мульти-AR: Project + ProjectMembership + Board + системные ProjectRole.

    Кросс-BC авторизация: caller должен обладать workspace-разрешением
    «projects.create» (либо каскадно через орг-роль — «workspaces.projects.create»).
    """

    REQUIRED_WORKSPACE_PERMISSION = "projects.create"

    def __init__(
        self,
        project_repo: ProjectRepository,
        membership_repo: ProjectMembershipRepository,
        board_repo: BoardRepository,
        project_role_repo: ProjectRoleRepository,
        identity_port: IdentityUserPort,
        workspace_port: WorkspacePort,
        workspace_permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._project_repo = project_repo
        self._membership_repo = membership_repo
        self._board_repo = board_repo
        self._project_role_repo = project_role_repo
        self._identity_port = identity_port
        self._workspace_port = workspace_port
        self._workspace_permission_checker = workspace_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: CreateProjectCommand) -> ProjectDTO:
        if not await self._workspace_port.workspace_exists(command.workspace_id):
            raise ValueError(f"Workspace не найден: {command.workspace_id}")

        has_perm = await self._workspace_permission_checker.has_permission(
            user_id=command.caller_id,
            workspace_id=command.workspace_id,
            permission=self.REQUIRED_WORKSPACE_PERMISSION,
        )
        if not has_perm:
            raise InsufficientProjectPermissionsException(
                permission=self.REQUIRED_WORKSPACE_PERMISSION,
                project_id=command.workspace_id,
            )

        if not await self._identity_port.user_exists(command.owner_id):
            raise UserNotFoundException(command.owner_id)

        owner_id = Id.from_string(command.owner_id)
        workspace_id = Id.from_string(command.workspace_id)
        methodology = Methodology(command.methodology)

        project = Project.create(
            name=command.name,
            workspace_id=workspace_id,
            owner_id=owner_id,
            methodology=methodology,
        )

        membership = ProjectMembership.create(
            project_id=project.id,
            owner_id=owner_id,
        )

        board = Board.create(
            project_id=project.id,
            methodology=methodology,
        )

        system_roles = build_system_project_roles(project.id)

        await self._project_repo.add(project)
        await self._membership_repo.add(membership)
        await self._board_repo.add(board)
        for role in system_roles:
            await self._project_role_repo.add(role)
        await self._event_bus.publish_all(project.clear_domain_events())
        await self._event_bus.publish_all(membership.clear_domain_events())
        for role in system_roles:
            await self._event_bus.publish_all(role.clear_domain_events())

        return ProjectDTO(
            id=str(project.id),
            workspace_id=str(project.workspace_id) if project.workspace_id else None,
            name=project.name,
            methodology=project.methodology.value,
            methodology_capabilities={
                "has_sprints": project.methodology_capabilities.has_sprints,
                "has_backlog": project.methodology_capabilities.has_backlog,
                "has_milestones": project.methodology_capabilities.has_milestones,
                "has_epics": project.methodology_capabilities.has_epics,
                "has_wip_limits": project.methodology_capabilities.has_wip_limits,
                "has_velocity": project.methodology_capabilities.has_velocity,
                "has_retros": project.methodology_capabilities.has_retros,
                "has_burndown": project.methodology_capabilities.has_burndown,
            },
            visibility=project.visibility.value,
            status=project.status.value,
            owner_ids=[str(oid) for oid in project.owner_ids],
            created_at=project.created_at,
            updated_at=project.updated_at,
        )
