"""Интеграционные тесты UpdateOrgRoleHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.update_org_role import (
    UpdateOrgRoleCommand,
    UpdateOrgRoleHandler,
)


@pytest.mark.integration
class TestUpdateOrgRoleHandler:
    @pytest.fixture
    def handler(self, org_role_repo, permission_checker_stub, event_bus_stub):
        return UpdateOrgRoleHandler(
            role_repo=org_role_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_update_permissions(self, handler, make_org_role, org_role_repo) -> None:
        role = await make_org_role(permissions=["self.*"])
        cmd = UpdateOrgRoleCommand(
            caller_id=str(Id.generate()),
            org_id=str(role.org_id) if role.org_id else str(Id.generate()),
            role_id=str(role.id),
            permissions=["members.*", "content.*"],
        )
        await handler.handle(cmd)
        found = await org_role_repo.get_by_id(role.id)
        assert found is not None
        assert found.permissions == ["members.*", "content.*"]

    async def test_update_description(self, handler, make_org_role, org_role_repo) -> None:
        role = await make_org_role()
        cmd = UpdateOrgRoleCommand(
            caller_id=str(Id.generate()),
            org_id=str(role.org_id) if role.org_id else str(Id.generate()),
            role_id=str(role.id),
            description="updated desc",
        )
        await handler.handle(cmd)
        found = await org_role_repo.get_by_id(role.id)
        assert found is not None
        assert found.description == "updated desc"
