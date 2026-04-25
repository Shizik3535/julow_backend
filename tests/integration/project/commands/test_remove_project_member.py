"""Интеграционные тесты RemoveProjectMemberHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.remove_project_member import (
    RemoveProjectMemberCommand,
    RemoveProjectMemberHandler,
)
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestRemoveProjectMemberHandler:
    """Тесты RemoveProjectMemberHandler."""

    @pytest.fixture
    def handler(self, project_repo, membership_repo, permission_checker_stub, event_bus_stub) -> RemoveProjectMemberHandler:
        return RemoveProjectMemberHandler(
            project_repo=project_repo,
            membership_repo=membership_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_remove_member_success(self, handler, membership_repo, make_project_with_membership, make_user) -> None:
        data = await make_project_with_membership()
        project = data["project"]
        membership = data["membership"]
        new_user = await make_user()
        role_id = data["system_roles"][0].id

        membership.add_member(user_id=new_user.id, role_id=role_id)
        membership.clear_domain_events()
        await membership_repo.update(membership)

        cmd = RemoveProjectMemberCommand(
            caller_id=str(data["owner_id"]),
            project_id=str(project.id),
            user_id=str(new_user.id),
        )
        await handler.handle(cmd)

        found = await membership_repo.get_by_project_id(project.id)
        assert found is not None
        assert not any(m.user_id == new_user.id and m.is_active for m in found.members)

    async def test_remove_member_not_found(self, handler) -> None:
        cmd = RemoveProjectMemberCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            user_id=str(Id.generate()),
        )
        with pytest.raises(ProjectNotFoundException):
            await handler.handle(cmd)
