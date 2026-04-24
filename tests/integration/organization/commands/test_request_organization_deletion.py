"""Интеграционные тесты RequestOrganizationDeletionHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.request_organization_deletion import (
    RequestOrganizationDeletionCommand,
    RequestOrganizationDeletionHandler,
)
from app.context.organization.domain.value_objects.org_status import OrgStatus


@pytest.mark.integration
class TestRequestOrganizationDeletionHandler:
    @pytest.fixture
    def handler(self, org_repo, permission_checker_stub, event_bus_stub):
        return RequestOrganizationDeletionHandler(
            org_repo=org_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_request_deletion(self, handler, make_org, org_repo) -> None:
        org = await make_org()
        cmd = RequestOrganizationDeletionCommand(
            caller_id=str(Id.generate()), org_id=str(org.id)
        )
        await handler.handle(cmd)
        found = await org_repo.get_by_id(org.id)
        assert found is not None
        assert found.status == OrgStatus.PENDING_DELETION
