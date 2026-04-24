"""
Workspace BC conftest — фикстуры для unit-тестов Workspace BC.

Содержит фабричные фикстуры для агрегатов, VOs и политик,
используемых в нескольких тестовых модулях.
"""

import pytest

from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.aggregates.workspace import Workspace
from app.context.workspace.domain.aggregates.workspace_invitation import WorkspaceInvitation
from app.context.workspace.domain.aggregates.workspace_membership import WorkspaceMembership
from app.context.workspace.domain.aggregates.workspace_role import WorkspaceRole
from app.context.workspace.domain.aggregates.workspace_team import WorkspaceTeam
from app.context.workspace.domain.value_objects.workspace_type import WorkspaceType
from tests.factories import EmailFactory, IdFactory


# ── Value Object фикстуры ─────────────────────────────────────────────────


@pytest.fixture
def any_workspace_id() -> Id:
    """Случайный workspace_id."""
    return IdFactory()


@pytest.fixture
def any_owner_id() -> Id:
    """Случайный owner_id."""
    return IdFactory()


@pytest.fixture
def any_role_id() -> Id:
    """Случайный role_id."""
    return IdFactory()


@pytest.fixture
def any_email() -> Email:
    """Случайный Email."""
    return EmailFactory()


# ── Агрегат Workspace ─────────────────────────────────────────────────────


@pytest.fixture
def new_workspace(any_owner_id: Id) -> Workspace:
    """Workspace после создания."""
    return Workspace.create(
        name="TestWS",
        owner_id=any_owner_id,
        workspace_type=WorkspaceType.TEAM,
    )


@pytest.fixture
def workspace(new_workspace: Workspace) -> Workspace:
    """Workspace с очищенными событиями (после создания)."""
    new_workspace.clear_domain_events()
    return new_workspace


@pytest.fixture
def archived_workspace(workspace: Workspace) -> Workspace:
    """Архивированный workspace."""
    workspace.archive()
    workspace.clear_domain_events()
    return workspace


@pytest.fixture
def suspended_workspace(workspace: Workspace) -> Workspace:
    """Приостановленный workspace."""
    workspace.suspend("test reason")
    workspace.clear_domain_events()
    return workspace


@pytest.fixture
def pending_deletion_workspace(workspace: Workspace) -> Workspace:
    """Workspace в процессе удаления."""
    workspace.request_deletion()
    workspace.clear_domain_events()
    return workspace


# ── Агрегат WorkspaceInvitation ───────────────────────────────────────────


@pytest.fixture
def email_invitation(
    any_workspace_id: Id, any_email: Email, any_role_id: Id, any_owner_id: Id
) -> WorkspaceInvitation:
    """Email-приглашение."""
    return WorkspaceInvitation.create_email_invitation(
        workspace_id=any_workspace_id,
        email=any_email,
        role_id=any_role_id,
        invited_by=any_owner_id,
    )


@pytest.fixture
def link_invitation(
    any_workspace_id: Id, any_role_id: Id, any_owner_id: Id
) -> WorkspaceInvitation:
    """Link-приглашение."""
    return WorkspaceInvitation.create_link_invitation(
        workspace_id=any_workspace_id,
        role_id=any_role_id,
        invited_by=any_owner_id,
        token_value="abc123",
    )


# ── Агрегат WorkspaceMembership ──────────────────────────────────────────


@pytest.fixture
def new_membership(any_workspace_id: Id, any_owner_id: Id) -> WorkspaceMembership:
    """Членство workspace после создания."""
    return WorkspaceMembership.create(
        workspace_id=any_workspace_id,
        owner_id=any_owner_id,
    )


@pytest.fixture
def membership(new_membership: WorkspaceMembership) -> WorkspaceMembership:
    """Членство с очищенными событиями (после создания)."""
    new_membership.clear_domain_events()
    return new_membership


# ── Агрегат WorkspaceRole ─────────────────────────────────────────────────


@pytest.fixture
def system_role() -> WorkspaceRole:
    """Системная роль."""
    return WorkspaceRole.create_system(
        name="owner",
        permissions=["*"],
        description="Owner role",
    )


@pytest.fixture
def custom_role(any_workspace_id: Id) -> WorkspaceRole:
    """Кастомная роль."""
    return WorkspaceRole.create_custom(
        workspace_id=any_workspace_id,
        name="custom_role",
        permissions=["read"],
    )


# ── Агрегат WorkspaceTeam ────────────────────────────────────────────────


@pytest.fixture
def new_team(any_workspace_id: Id) -> WorkspaceTeam:
    """Команда после создания."""
    return WorkspaceTeam.create(
        workspace_id=any_workspace_id,
        name="TestTeam",
    )


@pytest.fixture
def team(new_team: WorkspaceTeam) -> WorkspaceTeam:
    """Команда с очищенными событиями (после создания)."""
    new_team.clear_domain_events()
    return new_team


@pytest.fixture
def inactive_team(team: WorkspaceTeam) -> WorkspaceTeam:
    """Неактивная команда."""
    team.deactivate()
    team.clear_domain_events()
    return team
