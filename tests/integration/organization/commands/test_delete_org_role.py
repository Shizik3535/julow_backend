"""Интеграционные тесты DeleteOrgRoleHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.delete_org_role import (
    DeleteOrgRoleCommand,
    DeleteOrgRoleHandler,
)
from app.context.organization.domain.exceptions.org_role_exceptions import OrgRoleNotFoundException


@pytest.mark.integration
class TestDeleteOrgRoleHandler:
    @pytest.fixture
    def handler(self, org_role_repo, permission_checker_stub, event_bus_stub):
        return DeleteOrgRoleHandler(
            role_repo=org_role_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_delete_custom_role(self, handler, make_org_role, org_role_repo) -> None:
        role = await make_org_role(name="deletable-role")
        cmd = DeleteOrgRoleCommand(
            caller_id=str(Id.generate()),
            org_id=str(role.org_id) if role.org_id else str(Id.generate()),
            role_id=str(role.id),
        )
        await handler.handle(cmd)
        found = await org_role_repo.get_by_id(role.id)
        assert found is None
