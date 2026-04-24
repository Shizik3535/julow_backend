"""Интеграционные тесты ReactivateOrganizationHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.reactivate_organization import (
    ReactivateOrganizationCommand,
    ReactivateOrganizationHandler,
)
from app.context.organization.domain.value_objects.org_status import OrgStatus


@pytest.mark.integration
class TestReactivateOrganizationHandler:
    @pytest.fixture
    def handler(self, org_repo, permission_checker_stub, event_bus_stub):
        return ReactivateOrganizationHandler(
            org_repo=org_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_reactivate(self, handler, make_org, org_repo) -> None:
        org = await make_org()
        org.suspend(reason="test")
        org.clear_domain_events()
        await org_repo.update(org)

        cmd = ReactivateOrganizationCommand(
            caller_id=str(Id.generate()), org_id=str(org.id)
        )
        await handler.handle(cmd)
        found = await org_repo.get_by_id(org.id)
        assert found is not None
        assert found.status == OrgStatus.ACTIVE
