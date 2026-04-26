"""Интеграционные тесты AddProjectMemberHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.add_project_member import (
    AddProjectMemberCommand,
    AddProjectMemberHandler,
)
from app.context.project.application.exceptions.membership_app_exceptions import (
    MemberAlreadyExistsException,
    MemberNotInWorkspaceException,
    UserNotFoundException,
)
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _StubIdentityUserPort,
    _StubWorkspaceMembershipPort,
    _NoopEventBus,
)


@pytest.mark.integration
class TestAddProjectMemberHandler:
    """Тесты AddProjectMemberHandler."""

    @pytest.fixture
    def handler(self, project_repo, membership_repo, role_repo, permission_checker_stub, event_bus_stub) -> AddProjectMemberHandler:
        return AddProjectMemberHandler(
            project_repo=project_repo,
            membership_repo=membership_repo,
            role_repo=role_repo,
            identity_port=_StubIdentityUserPort(),
            workspace_membership_port=_StubWorkspaceMembershipPort(),
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_add_member_success(self, handler, membership_repo, make_project_with_membership, make_user) -> None:
        data = await make_project_with_membership()
        project = data["project"]
        new_user = await make_user()
        role_id = data["system_roles"][0].id

        cmd = AddProjectMemberCommand(
            caller_id=str(data["owner_id"]),
            project_id=str(project.id),
            user_id=str(new_user.id),
            role_id=str(role_id),
        )
        await handler.handle(cmd)

        membership = await membership_repo.get_by_project_id(project.id)
        assert membership is not None
        assert any(m.user_id == new_user.id for m in membership.members)

    async def test_add_member_user_not_found(self, project_repo, membership_repo, role_repo, permission_checker_stub, event_bus_stub) -> None:
        class _NoUserPort(_StubIdentityUserPort):
            async def user_exists(self, user_id: str) -> bool:
                return False

        handler = AddProjectMemberHandler(
            project_repo=project_repo,
            membership_repo=membership_repo,
            role_repo=role_repo,
            identity_port=_NoUserPort(),
            workspace_membership_port=_StubWorkspaceMembershipPort(),
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )
        cmd = AddProjectMemberCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            user_id=str(Id.generate()),
            role_id=str(Id.generate()),
        )
        with pytest.raises(UserNotFoundException):
            await handler.handle(cmd)

    async def test_add_member_not_workspace_member(self, project_repo, membership_repo, role_repo, permission_checker_stub, event_bus_stub, make_project_with_membership) -> None:
        class _NotWsMember(_StubWorkspaceMembershipPort):
            async def is_workspace_member(self, workspace_id: str, user_id: str) -> bool:
                return False

        data = await make_project_with_membership()
        handler = AddProjectMemberHandler(
            project_repo=project_repo,
            membership_repo=membership_repo,
            role_repo=role_repo,
            identity_port=_StubIdentityUserPort(),
            workspace_membership_port=_NotWsMember(),
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )
        new_user_id = str(Id.generate())
        cmd = AddProjectMemberCommand(
            caller_id=str(data["owner_id"]),
            project_id=str(data["project"].id),
            user_id=new_user_id,
            role_id=str(Id.generate()),
        )
        with pytest.raises(MemberNotInWorkspaceException):
            await handler.handle(cmd)
