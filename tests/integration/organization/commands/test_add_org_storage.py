"""Интеграционные тесты AddOrgStorageHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.add_org_storage import (
    AddOrgStorageCommand,
    AddOrgStorageHandler,
)
from app.context.organization.application.dto.storage_integration_dto import StorageIntegrationDTO


@pytest.mark.integration
class TestAddOrgStorageHandler:
    @pytest.fixture
    def handler(self, storage_repo, org_repo, encryption_stub, permission_checker_stub, event_bus_stub):
        return AddOrgStorageHandler(
            storage_repo=storage_repo,
            org_repo=org_repo,
            encryption_port=encryption_stub,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_add_local_storage(self, handler, make_org) -> None:
        org = await make_org()
        cmd = AddOrgStorageCommand(
            caller_id=str(Id.generate()),
            org_id=str(org.id),
            provider="local",
        )
        result = await handler.handle(cmd)
        assert isinstance(result, StorageIntegrationDTO)
        assert result.provider == "local"

    async def test_add_s3_storage_with_encrypted_key(self, handler, make_org, storage_repo) -> None:
        org = await make_org()
        cmd = AddOrgStorageCommand(
            caller_id=str(Id.generate()),
            org_id=str(org.id),
            provider="aws_s3",
            endpoint="https://minio.example.com",
            bucket="test-bucket",
            region="us-east-1",
            access_key="my-secret-key",
            max_bytes=2147483647,
        )
        result = await handler.handle(cmd)
        storage = await storage_repo.get_by_id(Id.from_string(result.id))
        assert storage is not None
        assert storage.config.access_key.startswith("enc:")

    async def test_add_with_quota(self, handler, make_org) -> None:
        org = await make_org()
        cmd = AddOrgStorageCommand(
            caller_id=str(Id.generate()),
            org_id=str(org.id),
            max_bytes=2147483647,
            max_file_size_bytes=104857600,
            allowed_extensions=[".pdf", ".docx"],
        )
        result = await handler.handle(cmd)
        assert result.max_bytes == 2147483647
