"""Интеграционные тесты AddOrgOwnerHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.add_org_owner import (
    AddOrgOwnerCommand,
    AddOrgOwnerHandler,
)


@pytest.mark.integration
class TestAddOrgOwnerHandler:
    @pytest.fixture
    def handler(self, org_repo, permission_checker_stub, event_bus_stub):
        return AddOrgOwnerHandler(
            org_repo=org_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_add_owner(self, handler, make_org, org_repo) -> None:
        org = await make_org()
        new_owner = Id.generate()
        cmd = AddOrgOwnerCommand(
            caller_id=str(Id.generate()), org_id=str(org.id), user_id=str(new_owner)
        )
        await handler.handle(cmd)
        found = await org_repo.get_by_id(org.id)
        assert found is not None
        assert new_owner in found.owner_ids
