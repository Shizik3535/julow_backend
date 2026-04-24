"""
Project BC conftest — фикстуры для unit-тестов Project BC.

Содержит фабричные фикстуры для агрегатов и VOs,
используемых в нескольких тестовых модулях.
"""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.value_objects.methodology import Methodology
from app.context.project.domain.aggregates.project import Project
from app.context.project.domain.aggregates.board import Board
from app.context.project.domain.aggregates.epic import Epic
from app.context.project.domain.aggregates.project_membership import ProjectMembership
from app.context.project.domain.aggregates.project_role import ProjectRole
from app.context.project.domain.aggregates.sprint import Sprint
from app.context.project.domain.aggregates.retro_template import RetroTemplate
from app.context.project.domain.value_objects.retro_section import RetroSection
from tests.factories import IdFactory


# ── Value Object фикстуры ─────────────────────────────────────────────────


@pytest.fixture
def any_workspace_id() -> Id:
    """Случайный Id workspace."""
    return IdFactory()


@pytest.fixture
def any_owner_id() -> Id:
    """Случайный Id владельца."""
    return IdFactory()


@pytest.fixture
def any_user_id() -> Id:
    """Случайный Id пользователя."""
    return IdFactory()


@pytest.fixture
def any_role_id() -> Id:
    """Случайный Id роли."""
    return IdFactory()


# ── Агрегат Project ───────────────────────────────────────────────────────


@pytest.fixture
def new_project(any_workspace_id: Id, any_owner_id: Id) -> Project:
    """Проект через Project.create()."""
    return Project.create(
        name="Test Project",
        workspace_id=any_workspace_id,
        owner_id=any_owner_id,
        methodology=Methodology.KANBAN,
    )


@pytest.fixture
def project(new_project: Project) -> Project:
    """Проект с очищенными событиями."""
    new_project.clear_domain_events()
    return new_project


@pytest.fixture
def archived_project(project: Project) -> Project:
    """Проект в статусе ARCHIVED."""
    project.archive()
    project.clear_domain_events()
    return project


@pytest.fixture
def suspended_project(project: Project) -> Project:
    """Проект в статусе SUSPENDED."""
    project.suspend(reason="Test suspension")
    project.clear_domain_events()
    return project


@pytest.fixture
def pending_deletion_project(project: Project) -> Project:
    """Проект в статусе PENDING_DELETION."""
    project.request_deletion()
    project.clear_domain_events()
    return project


# ── Агрегат Board ─────────────────────────────────────────────────────────


@pytest.fixture
def new_board() -> Board:
    """Доска через Board.create()."""
    return Board.create(project_id=IdFactory(), methodology=Methodology.KANBAN)


@pytest.fixture
def board(new_board: Board) -> Board:
    """Доска с очищенными событиями."""
    new_board.clear_domain_events()
    return new_board


# ── Агрегат Epic ──────────────────────────────────────────────────────────


@pytest.fixture
def new_epic() -> Epic:
    """Эпик через Epic.create()."""
    return Epic.create(project_id=IdFactory(), name="Test Epic", owner_id=IdFactory())


@pytest.fixture
def epic(new_epic: Epic) -> Epic:
    """Эпик с очищенными событиями."""
    new_epic.clear_domain_events()
    return new_epic


# ── Агрегат ProjectMembership ─────────────────────────────────────────────


@pytest.fixture
def new_membership() -> ProjectMembership:
    """Членство через ProjectMembership.create()."""
    return ProjectMembership.create(project_id=IdFactory(), owner_id=IdFactory())


@pytest.fixture
def membership(new_membership: ProjectMembership) -> ProjectMembership:
    """Членство с очищенными событиями."""
    new_membership.clear_domain_events()
    return new_membership


# ── Агрегат Sprint ────────────────────────────────────────────────────────


@pytest.fixture
def new_sprint() -> Sprint:
    """Спринт через Sprint.create()."""
    return Sprint.create(name="Sprint 1", project_id=IdFactory())


@pytest.fixture
def sprint(new_sprint: Sprint) -> Sprint:
    """Спринт с очищенными событиями."""
    new_sprint.clear_domain_events()
    return new_sprint


@pytest.fixture
def active_sprint(sprint: Sprint) -> Sprint:
    """Спринт в статусе ACTIVE."""
    sprint.start()
    sprint.clear_domain_events()
    return sprint


# ── Агрегат ProjectRole ───────────────────────────────────────────────────


@pytest.fixture
def system_role() -> ProjectRole:
    """Системная роль."""
    return ProjectRole.create_system(
        name="owner",
        permissions=["project:read", "project:write"],
        description="Project owner",
    )


@pytest.fixture
def custom_role() -> ProjectRole:
    """Кастомная роль."""
    return ProjectRole.create_custom(
        project_id=IdFactory(),
        name="custom_role",
        permissions=["project:read"],
    )


# ── Агрегат RetroTemplate ─────────────────────────────────────────────────


@pytest.fixture
def new_retro_template() -> RetroTemplate:
    """Кастомный шаблон ретроспективы."""
    sections = [
        RetroSection(title="What went well"),
        RetroSection(title="What can be improved"),
    ]
    return RetroTemplate.create_custom(name="Custom Retro", sections=sections)


@pytest.fixture
def retro_template(new_retro_template: RetroTemplate) -> RetroTemplate:
    """Шаблон с очищенными событиями."""
    new_retro_template.clear_domain_events()
    return new_retro_template
