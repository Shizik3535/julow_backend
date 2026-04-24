"""Интеграционные тесты UpdateOrgStorageHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.update_org_storage import (
    UpdateOrgStorageCommand,
    UpdateOrgStorageHandler,
)


@pytest.mark.integration
class TestUpdateOrgStorageHandler:
    @pytest.fixture
    def handler(self, storage_repo, encryption_stub, permission_checker_stub, event_bus_stub):
        return UpdateOrgStorageHandler(
            storage_repo=storage_repo,
            encryption_port=encryption_stub,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_update_quota(self, handler, make_storage_integration, storage_repo) -> None:
        storage = await make_storage_integration()
        cmd = UpdateOrgStorageCommand(
            caller_id=str(Id.generate()),
            org_id=str(storage.org_id),
            storage_id=str(storage.id),
            max_bytes=2147483647,
        )
        await handler.handle(cmd)
        found = await storage_repo.get_by_id(storage.id)
        assert found is not None
        assert found.quota.max_bytes == 2147483647

    async def test_update_config(self, handler, make_storage_integration, storage_repo) -> None:
        storage = await make_storage_integration()
        cmd = UpdateOrgStorageCommand(
            caller_id=str(Id.generate()),
            org_id=str(storage.org_id),
            storage_id=str(storage.id),
            bucket="new-bucket",
        )
        await handler.handle(cmd)
        found = await storage_repo.get_by_id(storage.id)
        assert found is not None
        assert found.config.bucket == "new-bucket"

    async def test_update_access_key_encrypts(self, handler, make_storage_integration, storage_repo) -> None:
        storage = await make_storage_integration()
        cmd = UpdateOrgStorageCommand(
            caller_id=str(Id.generate()),
            org_id=str(storage.org_id),
            storage_id=str(storage.id),
            access_key="new-secret-key",
        )
        await handler.handle(cmd)
        found = await storage_repo.get_by_id(storage.id)
        assert found is not None
        assert found.config.access_key.startswith("enc:")
