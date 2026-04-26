"""Интеграционные тесты CreateOrgRoleHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.create_org_role import (
    CreateOrgRoleCommand,
    CreateOrgRoleHandler,
)
from app.context.organization.application.dto.org_role_dto import OrgRoleDTO


@pytest.mark.integration
class TestCreateOrgRoleHandler:
    @pytest.fixture
    def handler(self, org_role_repo, org_repo, permission_checker_stub, event_bus_stub):
        return CreateOrgRoleHandler(
            role_repo=org_role_repo,
            org_repo=org_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_create_role(self, handler, make_org) -> None:
        org = await make_org()
        cmd = CreateOrgRoleCommand(
            caller_id=str(Id.generate()),
            org_id=str(org.id),
            name="editor",
            permissions=["teams.*"],
            scope="org",
            description="Team manager",
        )
        result = await handler.handle(cmd)
        assert isinstance(result, OrgRoleDTO)
        assert result.name == "editor"
        assert result.permissions == ["teams.*"]
