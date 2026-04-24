"""Интеграционные тесты SuspendOrganizationHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.suspend_organization import (
    SuspendOrganizationCommand,
    SuspendOrganizationHandler,
)
from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException
from app.context.organization.domain.value_objects.org_status import OrgStatus


@pytest.mark.integration
class TestSuspendOrganizationHandler:
    @pytest.fixture
    def handler(self, org_repo, permission_checker_stub, event_bus_stub):
        return SuspendOrganizationHandler(
            org_repo=org_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_suspend(self, handler, make_org, org_repo) -> None:
        org = await make_org()
        cmd = SuspendOrganizationCommand(
            caller_id=str(Id.generate()), org_id=str(org.id), reason="violation"
        )
        await handler.handle(cmd)
        found = await org_repo.get_by_id(org.id)
        assert found is not None
        assert found.status == OrgStatus.SUSPENDED

    async def test_org_not_found_raises(self, handler) -> None:
        cmd = SuspendOrganizationCommand(
            caller_id=str(Id.generate()), org_id=str(Id.generate()), reason="x"
        )
        with pytest.raises(OrganizationNotFoundException):
            await handler.handle(cmd)
