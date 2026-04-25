"""
Workspace BC conftest — фикстуры для integration-тестов Workspace.

Предоставляет mappers, repositories, seed-хелперы и стабы.
"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.application.ports.integration.inboard.identity_user_port import IdentityUserPort
from app.context.workspace.application.ports.integration.inboard.organization_permission_checker_port import (
    OrganizationPermissionCheckerPort,
)

from app.context.identity.domain.aggregates.user import User
from app.context.identity.infrastructure.persistence.mappers.user_mapper import UserMapper
from app.context.identity.infrastructure.persistence.repositories.sql_user_repository import SqlUserRepository

from app.context.workspace.domain.aggregates.workspace import Workspace
from app.context.workspace.domain.aggregates.workspace_membership import WorkspaceMembership
from app.context.workspace.domain.aggregates.workspace_role import WorkspaceRole
from app.context.workspace.domain.aggregates.workspace_team import WorkspaceTeam
from app.context.workspace.domain.aggregates.workspace_invitation import WorkspaceInvitation
from app.context.workspace.domain.value_objects.workspace_type import WorkspaceType
from app.context.workspace.domain.value_objects.member_source import MemberSource

from app.context.workspace.infrastructure.persistence.mappers.workspace_mapper import WorkspaceMapper
from app.context.workspace.infrastructure.persistence.mappers.workspace_membership_mapper import WorkspaceMembershipMapper
from app.context.workspace.infrastructure.persistence.mappers.workspace_role_mapper import WorkspaceRoleMapper
from app.context.workspace.infrastructure.persistence.mappers.workspace_team_mapper import WorkspaceTeamMapper
from app.context.workspace.infrastructure.persistence.mappers.workspace_invitation_mapper import WorkspaceInvitationMapper

from app.context.workspace.infrastructure.persistence.repositories.sql_workspace_repository import SqlWorkspaceRepository
from app.context.workspace.infrastructure.persistence.repositories.sql_workspace_membership_repository import (
    SqlWorkspaceMembershipRepository,
)
from app.context.workspace.infrastructure.persistence.repositories.sql_workspace_role_repository import SqlWorkspaceRoleRepository
from app.context.workspace.infrastructure.persistence.repositories.sql_workspace_team_repository import SqlWorkspaceTeamRepository
from app.context.workspace.infrastructure.persistence.repositories.sql_workspace_invitation_repository import (
    SqlWorkspaceInvitationRepository,
)

from app.context.workspace.infrastructure.persistence.seed.system_workspace_roles import SYSTEM_WORKSPACE_ROLES


# ── Identity Mappers & Repos (FK-зависимость) ──────────────────────────────


@pytest.fixture
def user_mapper() -> UserMapper:
    return UserMapper()


@pytest.fixture
def user_repo(db_session: AsyncSession, user_mapper: UserMapper) -> SqlUserRepository:
    return SqlUserRepository(session=db_session, mapper=user_mapper)


# ── Workspace Mappers ───────────────────────────────────────────────────────


@pytest.fixture
def workspace_mapper() -> WorkspaceMapper:
    return WorkspaceMapper()


@pytest.fixture
def workspace_membership_mapper() -> WorkspaceMembershipMapper:
    return WorkspaceMembershipMapper()


@pytest.fixture
def workspace_role_mapper() -> WorkspaceRoleMapper:
    return WorkspaceRoleMapper()


@pytest.fixture
def workspace_team_mapper() -> WorkspaceTeamMapper:
    return WorkspaceTeamMapper()


@pytest.fixture
def workspace_invitation_mapper() -> WorkspaceInvitationMapper:
    return WorkspaceInvitationMapper()


# ── Workspace Repositories ──────────────────────────────────────────────────


@pytest.fixture
def ws_repo(db_session: AsyncSession, workspace_mapper: WorkspaceMapper) -> SqlWorkspaceRepository:
    return SqlWorkspaceRepository(session=db_session, mapper=workspace_mapper)


@pytest.fixture
def ws_membership_repo(
    db_session: AsyncSession, workspace_membership_mapper: WorkspaceMembershipMapper
) -> SqlWorkspaceMembershipRepository:
    return SqlWorkspaceMembershipRepository(session=db_session, mapper=workspace_membership_mapper)


@pytest.fixture
def ws_role_repo(db_session: AsyncSession, workspace_role_mapper: WorkspaceRoleMapper) -> SqlWorkspaceRoleRepository:
    return SqlWorkspaceRoleRepository(session=db_session, mapper=workspace_role_mapper)


@pytest.fixture
def ws_team_repo(db_session: AsyncSession, workspace_team_mapper: WorkspaceTeamMapper) -> SqlWorkspaceTeamRepository:
    return SqlWorkspaceTeamRepository(session=db_session, mapper=workspace_team_mapper)


@pytest.fixture
def ws_invitation_repo(
    db_session: AsyncSession, workspace_invitation_mapper: WorkspaceInvitationMapper
) -> SqlWorkspaceInvitationRepository:
    return SqlWorkspaceInvitationRepository(session=db_session, mapper=workspace_invitation_mapper)


# ── Seed Helpers ─────────────────────────────────────────────────────────────


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
        email_vo = Email(f"auto-ws-{uuid.uuid4().hex[:8]}@test.com")
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
        email_vo = Email(email or f"ws-user-{uuid.uuid4().hex[:8]}@test.com")
        user = User(id=Id.generate(), email=email_vo)
        user.clear_domain_events()
        await user_repo.add(user)
        return user

    return _make


@pytest.fixture
def make_workspace(ws_repo: SqlWorkspaceRepository, _ensure_user):
    """Фабрика: создаёт Workspace с владельцем и сохраняет в БД."""

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
def make_workspace_with_membership(
    ws_repo: SqlWorkspaceRepository,
    ws_membership_repo: SqlWorkspaceMembershipRepository,
    ws_role_repo: SqlWorkspaceRoleRepository,
    _ensure_user,
):
    """
    Фабрика: создаёт Workspace + Membership + системные WorkspaceRole
    с владельцем как первым участником с ролью owner.
    """

    async def _make(
        name: str | None = None,
        owner_id: Id | None = None,
        workspace_type: WorkspaceType = WorkspaceType.TEAM,
        organization_id: Id | None = None,
    ) -> dict:
        oid = owner_id or Id.generate()
        await _ensure_user(oid)
        ws_name = name or f"ws-{uuid.uuid4().hex[:6]}"

        ws = Workspace.create(
            name=ws_name,
            owner_id=oid,
            workspace_type=workspace_type,
            organization_id=organization_id,
        )
        ws.clear_domain_events()
        await ws_repo.add(ws)

        owner_role: WorkspaceRole | None = None
        for seed_role in SYSTEM_WORKSPACE_ROLES:
            role = await ws_role_repo.get_by_name(seed_role["name"])
            if seed_role["name"] == "owner":
                owner_role = role

        membership = WorkspaceMembership.create(
            workspace_id=ws.id,
            owner_id=oid,
        )
        membership.clear_domain_events()
        await ws_membership_repo.add(membership)

        return {
            "workspace": ws,
            "membership": membership,
            "owner_role": owner_role,
            "owner_id": oid,
        }

    return _make


@pytest.fixture
def make_workspace_role(ws_role_repo: SqlWorkspaceRoleRepository, make_workspace):
    """Фабрика: создаёт кастомную WorkspaceRole и сохраняет в БД."""

    async def _make(
        workspace_id: Id | None = None,
        name: str | None = None,
        permissions: list[str] | None = None,
        description: str | None = None,
    ) -> WorkspaceRole:
        if workspace_id is None:
            ws = await make_workspace()
            workspace_id = ws.id
        role_name = name or f"custom-role-{uuid.uuid4().hex[:6]}"
        role = WorkspaceRole.create_custom(
            workspace_id=workspace_id,
            name=role_name,
            permissions=permissions or ["members.read"],
            description=description,
        )
        role.clear_domain_events()
        await ws_role_repo.add(role)
        return role

    return _make


@pytest.fixture
def make_workspace_team(ws_team_repo: SqlWorkspaceTeamRepository, make_workspace):
    """Фабрика: создаёт WorkspaceTeam и сохраняет в БД."""

    async def _make(
        workspace_id: Id | None = None,
        name: str | None = None,
        lead_id: Id | None = None,
    ) -> WorkspaceTeam:
        if workspace_id is None:
            ws = await make_workspace()
            workspace_id = ws.id
        team_name = name or f"team-{uuid.uuid4().hex[:6]}"
        team = WorkspaceTeam.create(
            workspace_id=workspace_id,
            name=team_name,
            lead_id=lead_id,
        )
        team.clear_domain_events()
        await ws_team_repo.add(team)
        return team

    return _make


@pytest.fixture
def make_workspace_invitation(ws_invitation_repo: SqlWorkspaceInvitationRepository, make_workspace):
    """Фабрика: создаёт email-приглашение и сохраняет в БД."""

    async def _make(
        workspace_id: Id | None = None,
        email: str | None = None,
        role_id: Id | None = None,
        invited_by: Id | None = None,
    ) -> WorkspaceInvitation:
        if workspace_id is None:
            ws = await make_workspace()
            workspace_id = ws.id
        email_vo = Email(email or f"invite-{uuid.uuid4().hex[:8]}@test.com")
        inv = WorkspaceInvitation.create_email_invitation(
            workspace_id=workspace_id,
            email=email_vo,
            role_id=role_id or Id.generate(),
            invited_by=invited_by or Id.generate(),
        )
        inv.clear_domain_events()
        await ws_invitation_repo.add(inv)
        return inv

    return _make


@pytest.fixture
def make_link_invitation(ws_invitation_repo: SqlWorkspaceInvitationRepository, make_workspace):
    """Фабрика: создаёт link-приглашение и сохраняет в БД."""

    async def _make(
        workspace_id: Id | None = None,
        role_id: Id | None = None,
        invited_by: Id | None = None,
        token_value: str | None = None,
    ) -> WorkspaceInvitation:
        if workspace_id is None:
            ws = await make_workspace()
            workspace_id = ws.id
        token = token_value or f"link-{uuid.uuid4().hex[:12]}"
        inv = WorkspaceInvitation.create_link_invitation(
            workspace_id=workspace_id,
            role_id=role_id or Id.generate(),
            invited_by=invited_by or Id.generate(),
            token_value=token,
        )
        inv.clear_domain_events()
        await ws_invitation_repo.add(inv)
        return inv

    return _make


# ── Stubs for Command/Query Handler Tests ────────────────────────────────────


class _AlwaysAllowPermissionChecker(WorkspacePermissionCheckerPort):
    """Stub: всегда разрешает любые действия в workspace."""

    async def has_permission(self, user_id: Id, workspace_id: Id, permission: str) -> bool:
        return True

    async def require_permission(self, user_id: Id, workspace_id: Id, permission: str) -> None:
        pass


class _AlwaysAllowOrgPermissionChecker(OrganizationPermissionCheckerPort):
    """Stub: всегда разрешает любые действия в организации."""

    async def has_permission(self, user_id: str, org_id: str, permission: str) -> bool:
        return True


class _StubIdentityUserPort(IdentityUserPort):
    """Stub: считает, что все пользователи существуют."""

    async def user_exists(self, user_id: str) -> bool:
        return True

    async def get_user(self, user_id: str) -> dict | None:
        return {"id": user_id, "email": f"stub-{user_id}@test.com", "status": "active"}


class _NoopEventBus(DomainEventBus):
    """Stub: поглощает все события без публикации."""

    async def publish_all(self, events: list) -> None:
        pass

    async def publish(self, event) -> None:
        pass


@pytest.fixture
def permission_checker_stub() -> _AlwaysAllowPermissionChecker:
    return _AlwaysAllowPermissionChecker()


@pytest.fixture
def org_permission_checker_stub() -> _AlwaysAllowOrgPermissionChecker:
    return _AlwaysAllowOrgPermissionChecker()


@pytest.fixture
def identity_user_stub() -> _StubIdentityUserPort:
    return _StubIdentityUserPort()


@pytest.fixture
def event_bus_stub() -> _NoopEventBus:
    return _NoopEventBus()
