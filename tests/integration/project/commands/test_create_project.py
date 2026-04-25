"""Интеграционные тесты CreateProjectHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.create_project import (
    CreateProjectCommand,
    CreateProjectHandler,
)
from app.context.project.application.exceptions.membership_app_exceptions import UserNotFoundException
from app.context.project.application.exceptions.authorization_exceptions import (
    InsufficientProjectPermissionsException,
)
from app.context.project.domain.value_objects.project_status import ProjectStatus
from tests.integration.project.conftest import (
    _AlwaysAllowWorkspacePermissionChecker,
    _StubIdentityUserPort,
    _StubWorkspacePort,
    _NoopEventBus,
)


@pytest.mark.integration
class TestCreateProjectHandler:
    """Тесты CreateProjectHandler — full stack."""

    @pytest.fixture
    def handler(self, project_repo, membership_repo, board_repo, role_repo) -> CreateProjectHandler:
        return CreateProjectHandler(
            project_repo=project_repo,
            membership_repo=membership_repo,
            board_repo=board_repo,
            project_role_repo=role_repo,
            identity_port=_StubIdentityUserPort(),
            workspace_port=_StubWorkspacePort(),
            workspace_permission_checker=_AlwaysAllowWorkspacePermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_create_project_success(self, handler, project_repo, make_user) -> None:
        user = await make_user()
        cmd = CreateProjectCommand(
            caller_id=str(user.id),
            name="New Project",
            workspace_id=str(Id.generate()),
            owner_id=str(user.id),
            methodology="kanban",
        )
        result = await handler.handle(cmd)

        assert result.name == "New Project"
        assert result.status == ProjectStatus.ACTIVE.value
        assert str(user.id) in result.owner_ids

        project = await project_repo.get_by_id(Id.from_string(result.id))
        assert project is not None

    async def test_create_project_with_scrum(self, handler, project_repo, make_user) -> None:
        user = await make_user()
        cmd = CreateProjectCommand(
            caller_id=str(user.id),
            name="Scrum Project",
            workspace_id=str(Id.generate()),
            owner_id=str(user.id),
            methodology="scrum",
        )
        result = await handler.handle(cmd)
        assert result.methodology == "scrum"

    async def test_create_project_creates_membership(self, handler, membership_repo, make_user) -> None:
        user = await make_user()
        cmd = CreateProjectCommand(
            caller_id=str(user.id),
            name="Membership Project",
            workspace_id=str(Id.generate()),
            owner_id=str(user.id),
        )
        result = await handler.handle(cmd)

        membership = await membership_repo.get_by_project_id(Id.from_string(result.id))
        assert membership is not None
        assert len(membership.members) >= 1

    async def test_create_project_creates_board(self, handler, board_repo, make_user) -> None:
        user = await make_user()
        cmd = CreateProjectCommand(
            caller_id=str(user.id),
            name="Board Project",
            workspace_id=str(Id.generate()),
            owner_id=str(user.id),
        )
        result = await handler.handle(cmd)

        board = await board_repo.get_by_project_id(Id.from_string(result.id))
        assert board is not None

    async def test_create_project_user_not_found(self, project_repo, membership_repo, board_repo, role_repo) -> None:
        class _NoUserPort(_StubIdentityUserPort):
            async def user_exists(self, user_id: str) -> bool:
                return False

        handler = CreateProjectHandler(
            project_repo=project_repo,
            membership_repo=membership_repo,
            board_repo=board_repo,
            project_role_repo=role_repo,
            identity_port=_NoUserPort(),
            workspace_port=_StubWorkspacePort(),
            workspace_permission_checker=_AlwaysAllowWorkspacePermissionChecker(),
            event_bus=_NoopEventBus(),
        )
        cmd = CreateProjectCommand(
            caller_id=str(Id.generate()),
            name="Fail Project",
            workspace_id=str(Id.generate()),
            owner_id=str(Id.generate()),
        )
        with pytest.raises(UserNotFoundException):
            await handler.handle(cmd)

    async def test_create_project_insufficient_workspace_permission(
        self, project_repo, membership_repo, board_repo, role_repo
    ) -> None:
        class _DenyWorkspaceChecker(_AlwaysAllowWorkspacePermissionChecker):
            async def has_permission(self, user_id: str, workspace_id: str, permission: str) -> bool:
                return False

        handler = CreateProjectHandler(
            project_repo=project_repo,
            membership_repo=membership_repo,
            board_repo=board_repo,
            project_role_repo=role_repo,
            identity_port=_StubIdentityUserPort(),
            workspace_port=_StubWorkspacePort(),
            workspace_permission_checker=_DenyWorkspaceChecker(),
            event_bus=_NoopEventBus(),
        )
        cmd = CreateProjectCommand(
            caller_id=str(Id.generate()),
            name="No Perm Project",
            workspace_id=str(Id.generate()),
            owner_id=str(Id.generate()),
        )
        with pytest.raises(InsufficientProjectPermissionsException):
            await handler.handle(cmd)
