"""Интеграционные тесты AddWorkspaceMemberHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.add_workspace_member import (
    AddWorkspaceMemberCommand,
    AddWorkspaceMemberHandler,
)
from app.context.workspace.application.exceptions.membership_app_exceptions import (
    MemberAlreadyExistsException,
    UserNotFoundException,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from tests.integration.workspace.conftest import (
    _AlwaysAllowPermissionChecker,
    _StubIdentityUserPort,
    _NoopEventBus,
)


@pytest.mark.integration
class TestAddWorkspaceMemberHandler:
    """Тесты AddWorkspaceMemberHandler."""

    @pytest.fixture
    def handler(self, ws_membership_repo) -> AddWorkspaceMemberHandler:
        return AddWorkspaceMemberHandler(
            membership_repo=ws_membership_repo,
            identity_port=_StubIdentityUserPort(),
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_add_member_success(
        self, handler, ws_membership_repo, make_workspace_with_membership
    ) -> None:
        data = await make_workspace_with_membership()
        ws = data["workspace"]
        new_user = Id.generate()

        cmd = AddWorkspaceMemberCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            user_id=str(new_user),
            role_id=str(Id.generate()),
        )
        await handler.handle(cmd)

        membership = await ws_membership_repo.get_by_workspace_id(ws.id)
        assert membership is not None
        member = membership._find_member(new_user)
        assert member is not None

    async def test_add_member_already_exists(
        self, handler, make_workspace_with_membership
    ) -> None:
        data = await make_workspace_with_membership()
        ws = data["workspace"]
        owner_id = data["owner_id"]

        cmd = AddWorkspaceMemberCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            user_id=str(owner_id),
            role_id=str(Id.generate()),
        )
        with pytest.raises(MemberAlreadyExistsException):
            await handler.handle(cmd)

    async def test_add_member_user_not_found(self, ws_membership_repo) -> None:
        class _NoUserPort(_StubIdentityUserPort):
            async def user_exists(self, user_id: str) -> bool:
                return False

        handler = AddWorkspaceMemberHandler(
            membership_repo=ws_membership_repo,
            identity_port=_NoUserPort(),
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )
        cmd = AddWorkspaceMemberCommand(
            caller_id=str(Id.generate()),
            workspace_id=str(Id.generate()),
            user_id=str(Id.generate()),
            role_id=str(Id.generate()),
        )
        with pytest.raises(UserNotFoundException):
            await handler.handle(cmd)

    async def test_add_member_workspace_not_found(self, handler) -> None:
        cmd = AddWorkspaceMemberCommand(
            caller_id=str(Id.generate()),
            workspace_id=str(Id.generate()),
            user_id=str(Id.generate()),
            role_id=str(Id.generate()),
        )
        with pytest.raises(WorkspaceNotFoundException):
            await handler.handle(cmd)
