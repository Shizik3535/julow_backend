"""
Project BC conftest — фикстуры для integration-тестов Project.

Предоставляет mappers, repositories, seed-хелперы и стабы.
"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)
from app.context.project.application.ports.integration.inboard.identity_user_port import IdentityUserPort
from app.context.project.application.ports.integration.inboard.workspace_port import WorkspacePort
from app.context.project.application.ports.integration.inboard.workspace_membership_port import WorkspaceMembershipPort
from app.context.project.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)

from app.context.identity.domain.aggregates.user import User
from app.context.identity.infrastructure.persistence.mappers.user_mapper import UserMapper
from app.context.identity.infrastructure.persistence.repositories.sql_user_repository import SqlUserRepository

from app.context.project.domain.aggregates.project import Project
from app.context.project.domain.aggregates.board import Board
from app.context.project.domain.aggregates.project_membership import ProjectMembership
from app.context.project.domain.aggregates.project_role import ProjectRole
from app.context.project.domain.aggregates.sprint import Sprint
from app.context.project.domain.aggregates.epic import Epic
from app.context.project.domain.aggregates.retro_template import RetroTemplate
from app.context.project.domain.value_objects.methodology import Methodology
from app.context.project.domain.value_objects.sprint_goal import SprintGoal
from app.context.project.domain.value_objects.retro_section import RetroSection
from app.context.project.domain.value_objects.retro_item_type import RetroItemType

from app.context.project.infrastructure.persistence.mappers.project_mapper import ProjectMapper
from app.context.project.infrastructure.persistence.mappers.board_mapper import BoardMapper
from app.context.project.infrastructure.persistence.mappers.project_membership_mapper import ProjectMembershipMapper
from app.context.project.infrastructure.persistence.mappers.project_role_mapper import ProjectRoleMapper
from app.context.project.infrastructure.persistence.mappers.sprint_mapper import SprintMapper
from app.context.project.infrastructure.persistence.mappers.epic_mapper import EpicMapper
from app.context.project.infrastructure.persistence.mappers.retro_template_mapper import RetroTemplateMapper

from app.context.project.infrastructure.persistence.repositories.sql_project_repository import SqlProjectRepository
from app.context.project.infrastructure.persistence.repositories.sql_board_repository import SqlBoardRepository
from app.context.project.infrastructure.persistence.repositories.sql_project_membership_repository import (
    SqlProjectMembershipRepository,
)
from app.context.project.infrastructure.persistence.repositories.sql_project_role_repository import SqlProjectRoleRepository
from app.context.project.infrastructure.persistence.repositories.sql_sprint_repository import SqlSprintRepository
from app.context.project.infrastructure.persistence.repositories.sql_epic_repository import SqlEpicRepository
from app.context.project.infrastructure.persistence.repositories.sql_retro_template_repository import (
    SqlRetroTemplateRepository,
)

from app.context.project.infrastructure.persistence.seed.system_project_roles import SYSTEM_PROJECT_ROLES


# ── Identity Mappers & Repos (FK-зависимость) ──────────────────────────────


@pytest.fixture
def user_mapper() -> UserMapper:
    return UserMapper()


@pytest.fixture
def user_repo(db_session: AsyncSession, user_mapper: UserMapper) -> SqlUserRepository:
    return SqlUserRepository(session=db_session, mapper=user_mapper)


# ── Project Mappers ────────────────────────────────────────────────────────


@pytest.fixture
def project_mapper() -> ProjectMapper:
    return ProjectMapper()


@pytest.fixture
def board_mapper() -> BoardMapper:
    return BoardMapper()


@pytest.fixture
def project_membership_mapper() -> ProjectMembershipMapper:
    return ProjectMembershipMapper()


@pytest.fixture
def project_role_mapper() -> ProjectRoleMapper:
    return ProjectRoleMapper()


@pytest.fixture
def sprint_mapper() -> SprintMapper:
    return SprintMapper()


@pytest.fixture
def epic_mapper() -> EpicMapper:
    return EpicMapper()


@pytest.fixture
def retro_template_mapper() -> RetroTemplateMapper:
    return RetroTemplateMapper()


# ── Project Repositories ──────────────────────────────────────────────────


@pytest.fixture
def project_repo(db_session: AsyncSession, project_mapper: ProjectMapper) -> SqlProjectRepository:
    return SqlProjectRepository(session=db_session, mapper=project_mapper)


@pytest.fixture
def board_repo(db_session: AsyncSession, board_mapper: BoardMapper) -> SqlBoardRepository:
    return SqlBoardRepository(session=db_session, mapper=board_mapper)


@pytest.fixture
def membership_repo(
    db_session: AsyncSession, project_membership_mapper: ProjectMembershipMapper
) -> SqlProjectMembershipRepository:
    return SqlProjectMembershipRepository(session=db_session, mapper=project_membership_mapper)


@pytest.fixture
def role_repo(db_session: AsyncSession, project_role_mapper: ProjectRoleMapper) -> SqlProjectRoleRepository:
    return SqlProjectRoleRepository(session=db_session, mapper=project_role_mapper)


@pytest.fixture
def sprint_repo(db_session: AsyncSession, sprint_mapper: SprintMapper) -> SqlSprintRepository:
    return SqlSprintRepository(session=db_session, mapper=sprint_mapper)


@pytest.fixture
def epic_repo(db_session: AsyncSession, epic_mapper: EpicMapper) -> SqlEpicRepository:
    return SqlEpicRepository(session=db_session, mapper=epic_mapper)


@pytest.fixture
def retro_template_repo(
    db_session: AsyncSession, retro_template_mapper: RetroTemplateMapper
) -> SqlRetroTemplateRepository:
    return SqlRetroTemplateRepository(session=db_session, mapper=retro_template_mapper)


# ── Seed Helpers ──────────────────────────────────────────────────────────


@pytest.fixture
def _ensure_user(user_repo: SqlUserRepository):
    """Хелпер: гарантирует наличие User в БД для FK-зависимостей."""
    _created: set[Id] = set()

    async def _fn(user_id: Id | None = None) -> User:
        uid = user_id or Id.generate()
        found = await user_repo.get_by_id(uid)
        if found is not None:
            _created.add(uid)
            return found
        email_vo = Email(f"auto-proj-{uuid.uuid4().hex[:8]}@test.com")
        user = User(id=uid, email=email_vo)
        user.clear_domain_events()
        await user_repo.add(user)
        _created.add(uid)
        return user

    return _fn


@pytest.fixture
def make_user(user_repo: SqlUserRepository, _ensure_user):
    """Фабрика: создаёт User и сохраняет в БД."""

    async def _make(
        email: str | None = None,
    ) -> User:
        email_vo = Email(email or f"proj-user-{uuid.uuid4().hex[:8]}@test.com")
        user = User(id=Id.generate(), email=email_vo)
        user.clear_domain_events()
        await user_repo.add(user)
        return user

    return _make


@pytest.fixture
def make_project(project_repo: SqlProjectRepository, _ensure_user):
    """Фабрика: создаёт Project с владельцем и сохраняет в БД."""

    async def _make(
        name: str | None = None,
        owner_id: Id | None = None,
        workspace_id: Id | None = None,
        methodology: Methodology = Methodology.KANBAN,
    ) -> Project:
        oid = owner_id or Id.generate()
        await _ensure_user(oid)
        ws_id = workspace_id or Id.generate()
        proj_name = name or f"proj-{uuid.uuid4().hex[:6]}"
        project = Project.create(
            name=proj_name,
            workspace_id=ws_id,
            owner_id=oid,
            methodology=methodology,
        )
        project.clear_domain_events()
        await project_repo.add(project)
        return project

    return _make


@pytest.fixture
def make_project_with_membership(
    project_repo: SqlProjectRepository,
    membership_repo: SqlProjectMembershipRepository,
    role_repo: SqlProjectRoleRepository,
    board_repo: SqlBoardRepository,
    _ensure_user,
):
    """
    Фабрика: создаёт Project + Membership + Board + системные ProjectRole
    с владельцем как первым участником.
    """

    async def _make(
        name: str | None = None,
        owner_id: Id | None = None,
        workspace_id: Id | None = None,
        methodology: Methodology = Methodology.KANBAN,
    ) -> dict:
        oid = owner_id or Id.generate()
        await _ensure_user(oid)
        ws_id = workspace_id or Id.generate()
        proj_name = name or f"proj-{uuid.uuid4().hex[:6]}"

        project = Project.create(
            name=proj_name,
            workspace_id=ws_id,
            owner_id=oid,
            methodology=methodology,
        )
        project.clear_domain_events()
        await project_repo.add(project)

        membership = ProjectMembership.create(
            project_id=project.id,
            owner_id=oid,
        )
        membership.clear_domain_events()
        await membership_repo.add(membership)

        board = Board.create(
            project_id=project.id,
            methodology=methodology,
        )
        board.clear_domain_events()
        await board_repo.add(board)

        system_roles = [
            ProjectRole.create_custom(
                project_id=project.id,
                name=str(tmpl["name"]),
                permissions=list(tmpl["permissions"]),  # type: ignore[arg-type]
                description=tmpl["description"],  # type: ignore[arg-type]
            )
            for tmpl in SYSTEM_PROJECT_ROLES
        ]
        for role in system_roles:
            role.clear_domain_events()
            await role_repo.add(role)

        return {
            "project": project,
            "membership": membership,
            "board": board,
            "system_roles": system_roles,
            "owner_id": oid,
        }

    return _make


@pytest.fixture
def make_project_role(role_repo: SqlProjectRoleRepository, make_project):
    """Фабрика: создаёт кастомную ProjectRole и сохраняет в БД."""

    async def _make(
        project_id: Id | None = None,
        name: str | None = None,
        permissions: list[str] | None = None,
        description: str | None = None,
    ) -> ProjectRole:
        if project_id is None:
            proj = await make_project()
            project_id = proj.id
        role_name = name or f"custom-role-{uuid.uuid4().hex[:6]}"
        role = ProjectRole.create_custom(
            project_id=project_id,
            name=role_name,
            permissions=permissions or ["content.read"],
            description=description,
        )
        role.clear_domain_events()
        await role_repo.add(role)
        return role

    return _make


@pytest.fixture
def make_sprint(sprint_repo: SqlSprintRepository, make_project):
    """Фабрика: создаёт Sprint и сохраняет в БД."""

    async def _make(
        project_id: Id | None = None,
        name: str | None = None,
        goal: SprintGoal | None = None,
    ) -> Sprint:
        if project_id is None:
            proj = await make_project(methodology=Methodology.SCRUM)
            project_id = proj.id
        sprint_name = name or f"sprint-{uuid.uuid4().hex[:6]}"
        sprint = Sprint.create(
            name=sprint_name,
            project_id=project_id,
            goal=goal,
        )
        sprint.clear_domain_events()
        await sprint_repo.add(sprint)
        return sprint

    return _make


@pytest.fixture
def make_epic(epic_repo: SqlEpicRepository, make_project):
    """Фабрика: создаёт Epic и сохраняет в БД."""

    async def _make(
        project_id: Id | None = None,
        name: str | None = None,
        owner_id: Id | None = None,
    ) -> Epic:
        if project_id is None:
            proj = await make_project()
            project_id = proj.id
        epic_name = name or f"epic-{uuid.uuid4().hex[:6]}"
        epic = Epic.create(
            project_id=project_id,
            name=epic_name,
            owner_id=owner_id,
        )
        epic.clear_domain_events()
        await epic_repo.add(epic)
        return epic

    return _make


@pytest.fixture
def make_retro_template(retro_template_repo: SqlRetroTemplateRepository):
    """Фабрика: создаёт кастомный RetroTemplate и сохраняет в БД."""

    async def _make(
        name: str | None = None,
        sections: list[RetroSection] | None = None,
        is_system: bool = False,
    ) -> RetroTemplate:
        tmpl_name = name or f"retro-{uuid.uuid4().hex[:6]}"
        tmpl_sections = sections or [
            RetroSection(title="What went well", item_type=RetroItemType.POSITIVE),
            RetroSection(title="What to improve", item_type=RetroItemType.NEGATIVE),
        ]
        template = RetroTemplate.create_system(name=tmpl_name, sections=tmpl_sections) if is_system else RetroTemplate.create_custom(name=tmpl_name, sections=tmpl_sections)
        template.clear_domain_events()
        await retro_template_repo.add(template)
        return template

    return _make


# ── Stubs for Command/Query Handler Tests ──────────────────────────────────


class _AlwaysAllowProjectPermissionChecker(ProjectPermissionCheckerPort):
    """Stub: всегда разрешает любые действия в проекте."""

    async def has_permission(self, user_id: Id, project_id: Id, permission: str) -> bool:
        return True

    async def require_permission(self, user_id: Id, project_id: Id, permission: str) -> None:
        pass


class _AlwaysAllowWorkspacePermissionChecker(WorkspacePermissionCheckerPort):
    """Stub: всегда разрешает любые действия в workspace."""

    async def has_permission(self, user_id: str, workspace_id: str, permission: str) -> bool:
        return True

    async def require_permission(self, user_id: str, workspace_id: str, permission: str) -> None:
        pass


class _StubIdentityUserPort(IdentityUserPort):
    """Stub: считает, что все пользователи существуют."""

    async def user_exists(self, user_id: str) -> bool:
        return True

    async def get_user(self, user_id: str) -> dict | None:
        return {"id": user_id, "email": f"stub-{user_id}@test.com", "status": "active"}


class _StubWorkspacePort(WorkspacePort):
    """Stub: считает, что все workspace существуют."""

    async def workspace_exists(self, workspace_id: str) -> bool:
        return True

    async def get_workspace(self, workspace_id: str) -> dict | None:
        return {"id": workspace_id, "name": "Stub Workspace", "organization_id": None}


class _StubWorkspaceMembershipPort(WorkspaceMembershipPort):
    """Stub: считает, что все пользователи являются участниками workspace."""

    async def is_workspace_member(self, workspace_id: str, user_id: str) -> bool:
        return True


class _NoopEventBus(DomainEventBus):
    """Stub: поглощает все события без публикации."""

    async def publish_all(self, events: list) -> None:
        pass

    async def publish(self, event) -> None:
        pass


@pytest.fixture
def permission_checker_stub() -> _AlwaysAllowProjectPermissionChecker:
    return _AlwaysAllowProjectPermissionChecker()


@pytest.fixture
def workspace_permission_checker_stub() -> _AlwaysAllowWorkspacePermissionChecker:
    return _AlwaysAllowWorkspacePermissionChecker()


@pytest.fixture
def identity_user_stub() -> _StubIdentityUserPort:
    return _StubIdentityUserPort()


@pytest.fixture
def workspace_stub() -> _StubWorkspacePort:
    return _StubWorkspacePort()


@pytest.fixture
def workspace_membership_stub() -> _StubWorkspaceMembershipPort:
    return _StubWorkspaceMembershipPort()


@pytest.fixture
def event_bus_stub() -> _NoopEventBus:
    return _NoopEventBus()
