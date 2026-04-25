"""Интеграционные тесты ChangeProjectMemberRoleHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.change_project_member_role import (
    ChangeProjectMemberRoleCommand,
    ChangeProjectMemberRoleHandler,
)
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestChangeProjectMemberRoleHandler:
    """Тесты ChangeProjectMemberRoleHandler."""

    @pytest.fixture
    def handler(self, membership_repo, permission_checker_stub, event_bus_stub) -> ChangeProjectMemberRoleHandler:
        return ChangeProjectMemberRoleHandler(
            membership_repo=membership_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_change_member_role_success(self, handler, membership_repo, make_project_with_membership, make_user) -> None:
        data = await make_project_with_membership()
        project = data["project"]
        membership = data["membership"]
        new_user = await make_user()
        role_id = data["system_roles"][0].id
        new_role_id = data["system_roles"][1].id if len(data["system_roles"]) > 1 else Id.generate()

        membership.add_member(user_id=new_user.id, role_id=role_id)
        membership.clear_domain_events()
        await membership_repo.update(membership)

        cmd = ChangeProjectMemberRoleCommand(
            caller_id=str(data["owner_id"]),
            project_id=str(project.id),
            user_id=str(new_user.id),
            new_role_id=str(new_role_id),
        )
        await handler.handle(cmd)

        found = await membership_repo.get_by_project_id(project.id)
        assert found is not None

    async def test_change_member_role_not_found(self, handler) -> None:
        cmd = ChangeProjectMemberRoleCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            user_id=str(Id.generate()),
            new_role_id=str(Id.generate()),
        )
        with pytest.raises(ProjectNotFoundException):
            await handler.handle(cmd)
