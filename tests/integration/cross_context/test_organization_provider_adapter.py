"""Cross-context: OrganizationProviderAdapter — предоставляет данные организации другим BC."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.infrastructure.integration.outboard.organization_provider_adapter import (
    OrganizationProviderAdapter,
)


@pytest.mark.integration
class TestOrganizationProviderAdapter:
    @pytest.fixture
    def adapter(self, org_repo):
        return OrganizationProviderAdapter(repo=org_repo)

    async def test_get_organization_dto_found(self, adapter, make_org) -> None:
        org = await make_org(name="CrossCtxOrg")
        dto = await adapter.get_organization(str(org.id))
        assert dto is not None
        assert dto.name == "CrossCtxOrg"

    async def test_organization_exists(self, adapter, make_org) -> None:
        org = await make_org()
        assert await adapter.organization_exists(str(org.id)) is True
        assert await adapter.organization_exists(str(Id.generate())) is False

    async def test_get_organization_not_found(self, adapter) -> None:
        dto = await adapter.get_organization(str(Id.generate()))
        assert dto is None
