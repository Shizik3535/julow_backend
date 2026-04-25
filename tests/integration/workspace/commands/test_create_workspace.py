"""Интеграционные тесты CreateWorkspaceHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.create_workspace import (
    CreateWorkspaceCommand,
    CreateWorkspaceHandler,
)
from app.context.workspace.application.exceptions.authorization_exceptions import (
    InsufficientWorkspacePermissionsException,
)
from app.context.workspace.application.exceptions.membership_app_exceptions import UserNotFoundException
from app.context.workspace.domain.value_objects.workspace_status import WorkspaceStatus
from tests.integration.workspace.conftest import (
    _AlwaysAllowOrgPermissionChecker,
    _StubIdentityUserPort,
    _NoopEventBus,
)


@pytest.mark.integration
class TestCreateWorkspaceHandler:
    """Тесты CreateWorkspaceHandler."""

    @pytest.fixture
    def handler(self, ws_repo, ws_membership_repo) -> CreateWorkspaceHandler:
        return CreateWorkspaceHandler(
            ws_repo=ws_repo,
            membership_repo=ws_membership_repo,
            identity_port=_StubIdentityUserPort(),
            org_permission_checker=_AlwaysAllowOrgPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_create_workspace_success(self, handler, ws_repo, make_user) -> None:
        user = await make_user()
        cmd = CreateWorkspaceCommand(
            caller_id=str(user.id),
            name="New Workspace",
            owner_id=str(user.id),
            workspace_type="TEAM",
        )
        result = await handler.handle(cmd)

        assert result.name == "New Workspace"
        assert result.status == WorkspaceStatus.ACTIVE.value
        assert result.workspace_type == "team"
        assert str(user.id) in result.owner_ids

        ws = await ws_repo.get_by_id(Id.from_string(result.id))
        assert ws is not None

    async def test_create_workspace_with_organization(self, handler, ws_repo, make_user) -> None:
        user = await make_user()
        org_id = Id.generate()
        cmd = CreateWorkspaceCommand(
            caller_id=str(user.id),
            name="Org Workspace",
            owner_id=str(user.id),
            workspace_type="TEAM",
            organization_id=str(org_id),
        )
        result = await handler.handle(cmd)

        assert result.organization_id == str(org_id)
        ws = await ws_repo.get_by_id(Id.from_string(result.id))
        assert ws is not None
        assert ws.organization_id == org_id

    async def test_create_workspace_user_not_found(self, ws_repo, ws_membership_repo) -> None:
        class _NoUserPort(_StubIdentityUserPort):
            async def user_exists(self, user_id: str) -> bool:
                return False

        handler = CreateWorkspaceHandler(
            ws_repo=ws_repo,
            membership_repo=ws_membership_repo,
            identity_port=_NoUserPort(),
            org_permission_checker=_AlwaysAllowOrgPermissionChecker(),
            event_bus=_NoopEventBus(),
        )
        cmd = CreateWorkspaceCommand(
            caller_id=str(Id.generate()),
            name="Fail WS",
            owner_id=str(Id.generate()),
        )
        with pytest.raises(UserNotFoundException):
            await handler.handle(cmd)

    async def test_create_workspace_insufficient_org_permission(self, ws_repo, ws_membership_repo) -> None:
        class _DenyOrgChecker(_AlwaysAllowOrgPermissionChecker):
            async def has_permission(self, user_id: str, org_id: str, permission: str) -> bool:
                return False

        handler = CreateWorkspaceHandler(
            ws_repo=ws_repo,
            membership_repo=ws_membership_repo,
            identity_port=_StubIdentityUserPort(),
            org_permission_checker=_DenyOrgChecker(),
            event_bus=_NoopEventBus(),
        )
        cmd = CreateWorkspaceCommand(
            caller_id=str(Id.generate()),
            name="No Perm WS",
            owner_id=str(Id.generate()),
            organization_id=str(Id.generate()),
        )
        with pytest.raises(InsufficientWorkspacePermissionsException):
            await handler.handle(cmd)

    async def test_create_workspace_creates_membership(
        self, handler, ws_membership_repo, make_user
    ) -> None:
        user = await make_user()
        cmd = CreateWorkspaceCommand(
            caller_id=str(user.id),
            name="Membership WS",
            owner_id=str(user.id),
        )
        result = await handler.handle(cmd)

        membership = await ws_membership_repo.get_by_workspace_id(Id.from_string(result.id))
        assert membership is not None
        assert len(membership.members) == 1
