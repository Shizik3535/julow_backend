"""Интеграционные тесты RemoveOrgOwnerHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.remove_org_owner import (
    RemoveOrgOwnerCommand,
    RemoveOrgOwnerHandler,
)


@pytest.mark.integration
class TestRemoveOrgOwnerHandler:
    @pytest.fixture
    def handler(self, org_repo, permission_checker_stub, event_bus_stub):
        return RemoveOrgOwnerHandler(
            org_repo=org_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_remove_co_owner(self, handler, make_org, org_repo) -> None:
        owner1 = Id.generate()
        owner2 = Id.generate()
        org = await make_org(owner_id=owner1)
        org.add_owner(owner2)
        org.clear_domain_events()
        await org_repo.update(org)

        cmd = RemoveOrgOwnerCommand(
            caller_id=str(Id.generate()), org_id=str(org.id), user_id=str(owner2)
        )
        await handler.handle(cmd)
        found = await org_repo.get_by_id(org.id)
        assert found is not None
        assert owner2 not in found.owner_ids
        assert owner1 in found.owner_ids
