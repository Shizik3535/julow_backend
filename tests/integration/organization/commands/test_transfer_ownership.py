"""Интеграционные тесты TransferOwnershipHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.transfer_ownership import (
    TransferOwnershipCommand,
    TransferOwnershipHandler,
)


@pytest.mark.integration
class TestTransferOwnershipHandler:
    @pytest.fixture
    def handler(self, org_repo, permission_checker_stub, event_bus_stub):
        return TransferOwnershipHandler(
            org_repo=org_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_transfer(self, handler, make_org, org_repo) -> None:
        old_owner = Id.generate()
        new_owner = Id.generate()
        org = await make_org(owner_id=old_owner)

        cmd = TransferOwnershipCommand(
            caller_id=str(Id.generate()),
            org_id=str(org.id),
            from_id=str(old_owner),
            to_id=str(new_owner),
        )
        await handler.handle(cmd)
        found = await org_repo.get_by_id(org.id)
        assert found is not None
        assert new_owner in found.owner_ids
