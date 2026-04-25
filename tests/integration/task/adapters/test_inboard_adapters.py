"""Интеграционные тесты inboard-адаптеров Task BC (делегируют к Project/Identity BC).

Каждый адаптер тестируется со стабом outboard-порта целевого BC.
"""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.infrastructure.integration.inboard.project_adapter import ProjectAdapter
from app.context.task.infrastructure.integration.inboard.board_adapter import BoardAdapter
from app.context.task.infrastructure.integration.inboard.sprint_adapter import SprintAdapter
from app.context.task.infrastructure.integration.inboard.epic_adapter import EpicAdapter
from app.context.task.infrastructure.integration.inboard.identity_user_adapter import IdentityUserAdapter
from app.context.task.infrastructure.integration.inboard.project_membership_adapter import ProjectMembershipAdapter
from app.context.task.infrastructure.authorization.task_role_based_permission_checker import TaskRoleBasedPermissionChecker
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException

from app.context.project.application.dto.project_dto import ProjectDTO
from app.context.project.application.dto.sprint_dto import SprintDTO
from app.context.project.application.dto.epic_dto import EpicDTO
from datetime import datetime, timezone

from app.context.identity.application.dto.user_dto import UserDTO


# ── Stubs for outboard ports (other BCs) ─────────────────────────────────────


class _StubProjectProvider:
    """Stub: Project BC outboard port."""

    async def project_exists(self, project_id: str) -> bool:
        return True

    async def get_project(self, project_id: str) -> ProjectDTO | None:
        return ProjectDTO(id=project_id, name="Stub Project", status="active")

    async def is_project_active(self, project_id: str) -> bool:
        return True


class _StubBoardProvider:
    """Stub: Project BC Board outboard port."""

    async def get_workflow_statuses(self, project_id: str) -> list[dict]:
        return []

    async def get_default_status_id(self, project_id: str) -> str | None:
        return str(Id.generate())

    async def is_transition_allowed(self, project_id: str, from_status_id: str, to_status_id: str) -> bool:
        return True

    async def get_columns(self, project_id: str) -> list[dict]:
        return []


class _StubSprintProvider:
    """Stub: Project BC Sprint outboard port."""

    async def sprint_exists(self, sprint_id: str) -> bool:
        return True

    async def get_sprint(self, sprint_id: str) -> SprintDTO | None:
        return SprintDTO(id=sprint_id, name="Stub Sprint", status="active")

    async def get_active_sprint(self, project_id: str) -> SprintDTO | None:
        return None


class _StubEpicProvider:
    """Stub: Project BC Epic outboard port."""

    async def epic_exists(self, epic_id: str) -> bool:
        return True

    async def get_epic(self, epic_id: str) -> EpicDTO | None:
        return EpicDTO(id=epic_id, name="Stub Epic", status="active")


class _StubIdentityUserProvider:
    """Stub: Identity BC outboard port."""

    async def get_user(self, user_id: str) -> UserDTO | None:
        return UserDTO(id=user_id, email="stub@test.com", status="active", role_ids=[], is_email_confirmed=True, created_at=datetime.now(tz=timezone.utc), updated_at=datetime.now(tz=timezone.utc))

    async def user_exists(self, user_id: str) -> bool:
        return True


class _StubProjectMembershipProvider:
    """Stub: Project BC Membership outboard port."""

    async def is_project_member(self, project_id: str, user_id: str) -> bool:
        return True


class _StubProjectPermissionProvider:
    """Stub: Project BC Permission outboard port."""

    async def has_permission(self, user_id: str, project_id: str, permission: str) -> bool:
        return True


class _DenyPermissionProvider:
    """Stub: denies all permissions."""

    async def has_permission(self, user_id: str, project_id: str, permission: str) -> bool:
        return False


# ── Tests ────────────────────────────────────────────────────────────────────


@pytest.mark.integration
class TestProjectAdapter:
    """Тесты ProjectAdapter (inboard)."""

    async def test_project_exists(self) -> None:
        adapter = ProjectAdapter(project_provider=_StubProjectProvider())
        assert await adapter.project_exists(str(Id.generate())) is True

    async def test_get_project(self) -> None:
        adapter = ProjectAdapter(project_provider=_StubProjectProvider())
        result = await adapter.get_project(str(Id.generate()))
        assert result is not None
        assert result["status"] == "active"

    async def test_is_project_active(self) -> None:
        adapter = ProjectAdapter(project_provider=_StubProjectProvider())
        assert await adapter.is_project_active(str(Id.generate())) is True


@pytest.mark.integration
class TestBoardAdapter:
    """Тесты BoardAdapter (inboard)."""

    async def test_get_default_status_id(self) -> None:
        adapter = BoardAdapter(board_provider=_StubBoardProvider())
        result = await adapter.get_default_status_id(str(Id.generate()))
        assert result is not None

    async def test_is_transition_allowed(self) -> None:
        adapter = BoardAdapter(board_provider=_StubBoardProvider())
        assert await adapter.is_transition_allowed(str(Id.generate()), "a", "b") is True


@pytest.mark.integration
class TestSprintAdapter:
    """Тесты SprintAdapter (inboard)."""

    async def test_sprint_exists(self) -> None:
        adapter = SprintAdapter(sprint_provider=_StubSprintProvider())
        assert await adapter.sprint_exists(str(Id.generate())) is True

    async def test_get_sprint(self) -> None:
        adapter = SprintAdapter(sprint_provider=_StubSprintProvider())
        result = await adapter.get_sprint(str(Id.generate()))
        assert result is not None


@pytest.mark.integration
class TestEpicAdapter:
    """Тесты EpicAdapter (inboard)."""

    async def test_epic_exists(self) -> None:
        adapter = EpicAdapter(epic_provider=_StubEpicProvider())
        assert await adapter.epic_exists(str(Id.generate())) is True

    async def test_get_epic(self) -> None:
        adapter = EpicAdapter(epic_provider=_StubEpicProvider())
        result = await adapter.get_epic(str(Id.generate()))
        assert result is not None


@pytest.mark.integration
class TestIdentityUserAdapter:
    """Тесты IdentityUserAdapter (inboard)."""

    async def test_user_exists(self) -> None:
        adapter = IdentityUserAdapter(identity_user_provider=_StubIdentityUserProvider())
        assert await adapter.user_exists(str(Id.generate())) is True


@pytest.mark.integration
class TestProjectMembershipAdapter:
    """Тесты ProjectMembershipAdapter (inboard)."""

    async def test_is_project_member(self) -> None:
        adapter = ProjectMembershipAdapter(project_membership_provider=_StubProjectMembershipProvider())
        assert await adapter.is_project_member(str(Id.generate()), str(Id.generate())) is True


class _StubTaskRepo:
    """Stub: TaskRepository для проверки участия."""

    async def is_participant_in_project(self, project_id: Id, user_id: Id) -> bool:
        return False


class _StubParticipantTaskRepo:
    """Stub: пользователь является участником задач проекта."""

    async def is_participant_in_project(self, project_id: Id, user_id: Id) -> bool:
        return True


class _StubProjectMembershipPort:
    """Stub: ProjectMembershipPort."""

    async def is_project_member(self, project_id: str, user_id: str) -> bool:
        return True


@pytest.mark.integration
class TestTaskRoleBasedPermissionChecker:
    """Тесты TaskRoleBasedPermissionChecker (authorization)."""

    async def test_has_permission_allowed_via_project(self) -> None:
        checker = TaskRoleBasedPermissionChecker(
            task_repo=_StubTaskRepo(),
            project_membership_port=_StubProjectMembershipPort(),
            project_permission_provider=_StubProjectPermissionProvider(),
        )
        assert await checker.has_permission(str(Id.generate()), str(Id.generate()), "tasks.update") is True

    async def test_has_permission_allowed_via_participant(self) -> None:
        checker = TaskRoleBasedPermissionChecker(
            task_repo=_StubParticipantTaskRepo(),
            project_membership_port=_StubProjectMembershipPort(),
            project_permission_provider=_DenyPermissionProvider(),
        )
        assert await checker.has_permission(str(Id.generate()), str(Id.generate()), "tasks.read") is True

    async def test_has_permission_denied_for_non_participant_permission(self) -> None:
        """tasks.update не входит в _TASK_PARTICIPANT_PERMISSIONS, поэтому даже
        участник задачи не получит доступ без project-роли."""
        checker = TaskRoleBasedPermissionChecker(
            task_repo=_StubParticipantTaskRepo(),
            project_membership_port=_StubProjectMembershipPort(),
            project_permission_provider=_DenyPermissionProvider(),
        )
        assert await checker.has_permission(str(Id.generate()), str(Id.generate()), "tasks.update") is False

    async def test_require_permission_allowed(self) -> None:
        checker = TaskRoleBasedPermissionChecker(
            task_repo=_StubTaskRepo(),
            project_membership_port=_StubProjectMembershipPort(),
            project_permission_provider=_StubProjectPermissionProvider(),
        )
        await checker.require_permission(str(Id.generate()), str(Id.generate()), "tasks.update")

    async def test_require_permission_denied(self) -> None:
        checker = TaskRoleBasedPermissionChecker(
            task_repo=_StubTaskRepo(),
            project_membership_port=_StubProjectMembershipPort(),
            project_permission_provider=_DenyPermissionProvider(),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await checker.require_permission(str(Id.generate()), str(Id.generate()), "tasks.update")
