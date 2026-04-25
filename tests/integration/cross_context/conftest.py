"""
Cross-context conftest — фикстуры из Identity, Profile, Organization и Workspace BC.

Cross-context тесты требуют доступа к репозиториям и seed-хелперам
всех BC. Фикстуры дублируют те, что определены в отдельных conftest-ах,
чтобы не нарушать иерархию pytest conftest.
"""

import uuid

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id

# ── Identity ────────────────────────────────────────────────────────────────

from app.context.identity.domain.aggregates.role import Role
from app.context.identity.domain.aggregates.user import User
from app.context.identity.domain.value_objects.auth_provider import AuthProvider

from app.context.identity.infrastructure.persistence.mappers.role_mapper import RoleMapper
from app.context.identity.infrastructure.persistence.mappers.user_mapper import UserMapper
from app.context.identity.infrastructure.persistence.repositories.sql_role_repository import SqlRoleRepository
from app.context.identity.infrastructure.persistence.repositories.sql_user_repository import SqlUserRepository

# ── Profile ─────────────────────────────────────────────────────────────────

from app.context.profile.domain.aggregates.user_profile import UserProfile
from app.context.profile.infrastructure.persistence.mappers.user_profile_mapper import UserProfileMapper
from app.context.profile.infrastructure.persistence.repositories.sql_user_profile_repository import (
    SqlUserProfileRepository,
)

# ── Organization ────────────────────────────────────────────────────────────

from app.context.organization.domain.aggregates.organization import Organization
from app.context.organization.domain.aggregates.org_membership import OrgMembership
from app.context.organization.domain.aggregates.org_role import OrgRole
from app.context.organization.domain.value_objects.org_role_scope import OrgRoleScope
from app.context.organization.infrastructure.persistence.mappers.organization_mapper import OrganizationMapper
from app.context.organization.infrastructure.persistence.mappers.org_membership_mapper import OrgMembershipMapper
from app.context.organization.infrastructure.persistence.mappers.org_role_mapper import OrgRoleMapper
from app.context.organization.infrastructure.persistence.repositories.sql_organization_repository import (
    SqlOrganizationRepository,
)
from app.context.organization.infrastructure.persistence.repositories.sql_org_membership_repository import (
    SqlOrgMembershipRepository,
)
from app.context.organization.infrastructure.persistence.repositories.sql_org_role_repository import (
    SqlOrgRoleRepository,
)
from app.context.organization.infrastructure.persistence.seed.org_roles import SYSTEM_ORG_ROLES

# ── Workspace ───────────────────────────────────────────────────────────────

from app.context.workspace.domain.aggregates.workspace import Workspace
from app.context.workspace.domain.aggregates.workspace_membership import WorkspaceMembership
from app.context.workspace.domain.aggregates.workspace_role import WorkspaceRole
from app.context.workspace.domain.aggregates.workspace_team import WorkspaceTeam
from app.context.workspace.domain.aggregates.workspace_invitation import WorkspaceInvitation
from app.context.workspace.domain.value_objects.workspace_type import WorkspaceType
from app.context.workspace.domain.value_objects.member_source import MemberSource
from app.context.workspace.infrastructure.persistence.mappers.workspace_mapper import WorkspaceMapper
from app.context.workspace.infrastructure.persistence.mappers.workspace_membership_mapper import (
    WorkspaceMembershipMapper,
)
from app.context.workspace.infrastructure.persistence.mappers.workspace_role_mapper import WorkspaceRoleMapper
from app.context.workspace.infrastructure.persistence.mappers.workspace_team_mapper import WorkspaceTeamMapper
from app.context.workspace.infrastructure.persistence.mappers.workspace_invitation_mapper import (
    WorkspaceInvitationMapper,
)
from app.context.workspace.infrastructure.persistence.repositories.sql_workspace_repository import (
    SqlWorkspaceRepository,
)
from app.context.workspace.infrastructure.persistence.repositories.sql_workspace_membership_repository import (
    SqlWorkspaceMembershipRepository,
)
from app.context.workspace.infrastructure.persistence.repositories.sql_workspace_role_repository import (
    SqlWorkspaceRoleRepository,
)
from app.context.workspace.infrastructure.persistence.repositories.sql_workspace_team_repository import (
    SqlWorkspaceTeamRepository,
)
from app.context.workspace.infrastructure.persistence.repositories.sql_workspace_invitation_repository import (
    SqlWorkspaceInvitationRepository,
)


# ── Identity Mappers & Repos ────────────────────────────────────────────────


@pytest.fixture
def user_mapper() -> UserMapper:
    return UserMapper()


@pytest.fixture
def role_mapper() -> RoleMapper:
    return RoleMapper()


@pytest.fixture
def user_repo(db_session: AsyncSession, user_mapper: UserMapper) -> SqlUserRepository:
    return SqlUserRepository(session=db_session, mapper=user_mapper)


@pytest.fixture
def role_repo(db_session: AsyncSession, role_mapper: RoleMapper) -> SqlRoleRepository:
    return SqlRoleRepository(session=db_session, mapper=role_mapper)


# ── Profile Mapper & Repo ───────────────────────────────────────────────────


@pytest.fixture
def profile_mapper() -> UserProfileMapper:
    return UserProfileMapper()


@pytest.fixture
def profile_repo(db_session: AsyncSession, profile_mapper: UserProfileMapper) -> SqlUserProfileRepository:
    return SqlUserProfileRepository(session=db_session, mapper=profile_mapper)


# ── Identity Seed Helpers ───────────────────────────────────────────────────


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
        email_vo = Email(f"auto-{uuid.uuid4().hex[:8]}@test.com")
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
        auth_provider: AuthProvider = AuthProvider.EMAIL_PASSWORD,
    ) -> User:
        email_vo = Email(email or f"user-{uuid.uuid4().hex[:8]}@test.com")
        user = User.register(email=email_vo, auth_provider=auth_provider)
        user.clear_domain_events()
        await user_repo.add(user)
        return user

    return _make


@pytest.fixture
def make_role(role_repo: SqlRoleRepository):
    """Фабрика: создаёт Role и сохраняет в БД. Возвращает существующую роль по имени, если есть."""

    async def _make(
        name: str | None = None,
        permissions: list[str] | None = None,
        is_system: bool = False,
    ) -> Role:
        role_name = name or f"role-{uuid.uuid4().hex[:6]}"
        existing = await role_repo.get_by_name(role_name)
        if existing is not None:
            return existing
        role = Role(
            name=role_name,
            permissions=permissions or [],
            is_system=is_system,
        )
        await role_repo.add(role)
        return role

    return _make


# ── Profile Seed Helpers ────────────────────────────────────────────────────


@pytest.fixture
def make_profile(profile_repo: SqlUserProfileRepository):
    """Фабрика: создаёт UserProfile и сохраняет в БД."""

    async def _make(user_id: Id | None = None) -> UserProfile:
        uid = user_id or Id.generate()
        profile = UserProfile.create(user_id=uid)
        profile.clear_domain_events()
        await profile_repo.add(profile)
        return profile

    return _make


# ── Organization Mappers & Repos ─────────────────────────────────────────────


@pytest.fixture
def organization_mapper() -> OrganizationMapper:
    return OrganizationMapper()


@pytest.fixture
def org_membership_mapper() -> OrgMembershipMapper:
    return OrgMembershipMapper()


@pytest.fixture
def org_role_mapper() -> OrgRoleMapper:
    return OrgRoleMapper()


@pytest.fixture
def org_repo(db_session: AsyncSession, organization_mapper: OrganizationMapper) -> SqlOrganizationRepository:
    return SqlOrganizationRepository(session=db_session, mapper=organization_mapper)


@pytest.fixture
def membership_repo(
    db_session: AsyncSession, org_membership_mapper: OrgMembershipMapper
) -> SqlOrgMembershipRepository:
    return SqlOrgMembershipRepository(session=db_session, mapper=org_membership_mapper)


@pytest.fixture
def org_role_repo(db_session: AsyncSession, org_role_mapper: OrgRoleMapper) -> SqlOrgRoleRepository:
    return SqlOrgRoleRepository(session=db_session, mapper=org_role_mapper)


# ── Organization Seed Helpers ────────────────────────────────────────────────


@pytest.fixture
def make_org(org_repo: SqlOrganizationRepository, _ensure_user):
    """Фабрика: создаёт Organization с владельцем и сохраняет в БД."""

    async def _make(
        name: str | None = None,
        owner_id: Id | None = None,
    ) -> Organization:
        oid = owner_id or Id.generate()
        await _ensure_user(oid)
        org_name = name or f"org-{uuid.uuid4().hex[:6]}"
        org = Organization.create(name=org_name, owner_id=oid)
        org.clear_domain_events()
        await org_repo.add(org)
        return org

    return _make


@pytest.fixture
def make_org_with_membership(
    org_repo: SqlOrganizationRepository,
    membership_repo: SqlOrgMembershipRepository,
    org_role_repo: SqlOrgRoleRepository,
    _ensure_user,
):
    """Фабрика: создаёт Organization + 4 системных OrgRole + OrgMembership."""

    async def _make(
        name: str | None = None,
        owner_id: Id | None = None,
    ) -> dict:
        oid = owner_id or Id.generate()
        await _ensure_user(oid)
        org_name = name or f"org-{uuid.uuid4().hex[:6]}"

        org = Organization.create(name=org_name, owner_id=oid)
        org.clear_domain_events()
        await org_repo.add(org)

        owner_role: OrgRole | None = None
        for seed_role in SYSTEM_ORG_ROLES:
            role = OrgRole.create_custom(
                org_id=org.id,
                name=seed_role["name"],
                permissions=seed_role["permissions"],
                scope=OrgRoleScope(seed_role["scope"]),
                description=seed_role["description"],
            )
            role.is_system = True
            role.clear_domain_events()
            await org_role_repo.add(role)
            if seed_role["name"] == "owner":
                owner_role = role

        membership = OrgMembership.create(
            org_id=org.id,
            owner_id=oid,
            owner_role_id=owner_role.id if owner_role else Id.generate(),
        )
        membership.clear_domain_events()
        await membership_repo.add(membership)

        return {
            "org": org,
            "membership": membership,
            "owner_role": owner_role,
            "owner_id": oid,
        }

    return _make


# ── Workspace Mappers & Repos ────────────────────────────────────────────────


@pytest.fixture
def ws_mapper() -> WorkspaceMapper:
    return WorkspaceMapper()


@pytest.fixture
def ws_membership_mapper() -> WorkspaceMembershipMapper:
    return WorkspaceMembershipMapper()


@pytest.fixture
def ws_role_mapper() -> WorkspaceRoleMapper:
    return WorkspaceRoleMapper()


@pytest.fixture
def ws_team_mapper() -> WorkspaceTeamMapper:
    return WorkspaceTeamMapper()


@pytest.fixture
def ws_invitation_mapper() -> WorkspaceInvitationMapper:
    return WorkspaceInvitationMapper()


@pytest.fixture
def ws_repo(db_session: AsyncSession, ws_mapper: WorkspaceMapper) -> SqlWorkspaceRepository:
    return SqlWorkspaceRepository(session=db_session, mapper=ws_mapper)


@pytest.fixture
def ws_membership_repo(
    db_session: AsyncSession, ws_membership_mapper: WorkspaceMembershipMapper
) -> SqlWorkspaceMembershipRepository:
    return SqlWorkspaceMembershipRepository(session=db_session, mapper=ws_membership_mapper)


@pytest.fixture
def ws_role_repo(db_session: AsyncSession, ws_role_mapper: WorkspaceRoleMapper) -> SqlWorkspaceRoleRepository:
    return SqlWorkspaceRoleRepository(session=db_session, mapper=ws_role_mapper)


@pytest.fixture
def ws_team_repo(db_session: AsyncSession, ws_team_mapper: WorkspaceTeamMapper) -> SqlWorkspaceTeamRepository:
    return SqlWorkspaceTeamRepository(session=db_session, mapper=ws_team_mapper)


@pytest.fixture
def ws_invitation_repo(
    db_session: AsyncSession, ws_invitation_mapper: WorkspaceInvitationMapper
) -> SqlWorkspaceInvitationRepository:
    return SqlWorkspaceInvitationRepository(session=db_session, mapper=ws_invitation_mapper)


# ── Workspace Seed Helpers ──────────────────────────────────────────────────


@pytest.fixture
def make_ws(ws_repo: SqlWorkspaceRepository, _ensure_user):
    """Фабрика: создаёт Workspace и сохраняет в БД."""

    async def _make(
        name: str | None = None,
        owner_id: Id | None = None,
        workspace_type: WorkspaceType = WorkspaceType.TEAM,
        organization_id: Id | None = None,
        parent_workspace_id: Id | None = None,
    ) -> Workspace:
        oid = owner_id or Id.generate()
        await _ensure_user(oid)
        ws_name = name or f"ws-{uuid.uuid4().hex[:6]}"
        ws = Workspace.create(
            name=ws_name,
            owner_id=oid,
            workspace_type=workspace_type,
            organization_id=organization_id,
            parent_workspace_id=parent_workspace_id,
        )
        ws.clear_domain_events()
        await ws_repo.add(ws)
        return ws

    return _make


@pytest.fixture
def make_ws_with_membership(
    ws_repo: SqlWorkspaceRepository,
    ws_membership_repo: SqlWorkspaceMembershipRepository,
    _ensure_user,
):
    """Фабрика: создаёт Workspace + WorkspaceMembership."""

    async def _make(
        name: str | None = None,
        owner_id: Id | None = None,
        organization_id: Id | None = None,
    ) -> dict:
        oid = owner_id or Id.generate()
        await _ensure_user(oid)
        ws_name = name or f"ws-mem-{uuid.uuid4().hex[:6]}"
        ws = Workspace.create(
            name=ws_name,
            owner_id=oid,
            workspace_type=WorkspaceType.TEAM,
            organization_id=organization_id,
        )
        ws.clear_domain_events()
        await ws_repo.add(ws)

        membership = WorkspaceMembership.create(workspace_id=ws.id, owner_id=oid)
        membership.clear_domain_events()
        await ws_membership_repo.add(membership)

        return {"workspace": ws, "membership": membership, "owner_id": oid}

    return _make


# ── Project Mappers & Repos ──────────────────────────────────────────────────

from app.context.project.domain.aggregates.project import Project
from app.context.project.domain.aggregates.board import Board
from app.context.project.domain.aggregates.project_membership import ProjectMembership
from app.context.project.domain.aggregates.project_role import ProjectRole
from app.context.project.domain.value_objects.methodology import Methodology

from app.context.project.infrastructure.persistence.mappers.project_mapper import ProjectMapper
from app.context.project.infrastructure.persistence.mappers.board_mapper import BoardMapper
from app.context.project.infrastructure.persistence.mappers.project_membership_mapper import ProjectMembershipMapper
from app.context.project.infrastructure.persistence.mappers.project_role_mapper import ProjectRoleMapper

from app.context.project.infrastructure.persistence.repositories.sql_project_repository import SqlProjectRepository
from app.context.project.infrastructure.persistence.repositories.sql_board_repository import SqlBoardRepository
from app.context.project.infrastructure.persistence.repositories.sql_project_membership_repository import (
    SqlProjectMembershipRepository,
)
from app.context.project.infrastructure.persistence.repositories.sql_project_role_repository import SqlProjectRoleRepository

from app.context.project.infrastructure.persistence.seed.system_project_roles import SYSTEM_PROJECT_ROLES


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
def project_repo(db_session: AsyncSession, project_mapper: ProjectMapper) -> SqlProjectRepository:
    return SqlProjectRepository(session=db_session, mapper=project_mapper)


@pytest.fixture
def board_repo(db_session: AsyncSession, board_mapper: BoardMapper) -> SqlBoardRepository:
    return SqlBoardRepository(session=db_session, mapper=board_mapper)


@pytest.fixture
def proj_membership_repo(
    db_session: AsyncSession, project_membership_mapper: ProjectMembershipMapper
) -> SqlProjectMembershipRepository:
    return SqlProjectMembershipRepository(session=db_session, mapper=project_membership_mapper)


@pytest.fixture
def proj_role_repo(db_session: AsyncSession, project_role_mapper: ProjectRoleMapper) -> SqlProjectRoleRepository:
    return SqlProjectRoleRepository(session=db_session, mapper=project_role_mapper)


# ── Project Seed Helpers ────────────────────────────────────────────────────


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
    proj_membership_repo: SqlProjectMembershipRepository,
    proj_role_repo: SqlProjectRoleRepository,
    board_repo: SqlBoardRepository,
    _ensure_user,
):
    """Фабрика: создаёт Project + Membership + Board + системные ProjectRole."""

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
        await proj_membership_repo.add(membership)

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
            await proj_role_repo.add(role)

        return {
            "project": project,
            "membership": membership,
            "board": board,
            "system_roles": system_roles,
            "owner_id": oid,
        }

    return _make
