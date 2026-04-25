"""Интеграционные тесты GetOrgStorageHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.exceptions import EntityNotFoundException
from app.context.organization.application.dto.storage_integration_dto import StorageIntegrationDTO
from app.context.organization.application.queries.get_org_storage import (
    GetOrgStorageHandler,
    GetOrgStorageQuery,
)


@pytest.mark.integration
class TestGetOrgStorageHandler:
    @pytest.fixture
    def handler(self, storage_repo, permission_checker_stub) -> GetOrgStorageHandler:
        return GetOrgStorageHandler(storage_repo=storage_repo, org_permission_checker=permission_checker_stub)

    async def test_returns_storage_dto(self, handler, make_storage_integration) -> None:
        storage = await make_storage_integration()
        query = GetOrgStorageQuery(caller_id=str(Id.generate()), org_id=str(storage.org_id))
        result = await handler.handle(query)
        assert isinstance(result, StorageIntegrationDTO)
        assert result.org_id == str(storage.org_id)

    async def test_not_found_raises(self, handler) -> None:
        query = GetOrgStorageQuery(caller_id=str(Id.generate()), org_id=str(Id.generate()))
        with pytest.raises(EntityNotFoundException):
            await handler.handle(query)
