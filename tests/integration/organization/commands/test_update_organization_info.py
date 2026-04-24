"""Интеграционные тесты UpdateOrganizationInfoHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.update_organization_info import (
    UpdateOrganizationInfoCommand,
    UpdateOrganizationInfoHandler,
)
from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException


@pytest.mark.integration
class TestUpdateOrganizationInfoHandler:
    @pytest.fixture
    def handler(self, org_repo, permission_checker_stub, event_bus_stub):
        return UpdateOrganizationInfoHandler(
            org_repo=org_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_update_name(self, handler, make_org, org_repo) -> None:
        org = await make_org()
        cmd = UpdateOrganizationInfoCommand(
            caller_id=str(Id.generate()), org_id=str(org.id), name="NewName"
        )
        await handler.handle(cmd)
        found = await org_repo.get_by_id(org.id)
        assert found is not None
        assert found.name == "NewName"

    async def test_update_display_name(self, handler, make_org, org_repo) -> None:
        org = await make_org()
        cmd = UpdateOrganizationInfoCommand(
            caller_id=str(Id.generate()),
            org_id=str(org.id),
            personalization_display_name="My Org",
        )
        await handler.handle(cmd)
        found = await org_repo.get_by_id(org.id)
        assert found is not None
        assert found.personalization.display_name == "My Org"

    async def test_org_not_found_raises(self, handler) -> None:
        cmd = UpdateOrganizationInfoCommand(
            caller_id=str(Id.generate()), org_id=str(Id.generate()), name="X"
        )
        with pytest.raises(OrganizationNotFoundException):
            await handler.handle(cmd)
