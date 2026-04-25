"""
Интеграционные тесты OrganizationAdapter (inboard).

Адаптер делегирует в OrganizationProvider (outboard Organization BC).
Тестируем через stub provider, проверяя корректность маппинга DTO → dict.
"""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.organization_dto import OrganizationDTO
from app.context.organization.application.ports.integration.outboard.organization_provider import OrganizationProvider
from app.context.workspace.infrastructure.integration.inboard.organization_adapter import OrganizationAdapter


class _StubOrganizationProvider(OrganizationProvider):
    """Stub outboard-провайдер Organization BC."""

    def __init__(self, orgs: dict[str, OrganizationDTO] | None = None):
        self._orgs = orgs or {}

    async def get_organization(self, org_id: str) -> OrganizationDTO | None:
        return self._orgs.get(org_id)

    async def organization_exists(self, org_id: str) -> bool:
        return org_id in self._orgs


def _make_org_dto(org_id: str, name: str = "Test Org", status: str = "active") -> OrganizationDTO:
    from datetime import datetime, timezone
    return OrganizationDTO(
        id=org_id,
        name=name,
        status=status,
        owner_ids=[],
        personalization={},
        security_policy={},
        membership_policy={},
        created_at=datetime.now(tz=timezone.utc),
        updated_at=datetime.now(tz=timezone.utc),
    )


@pytest.mark.integration
class TestOrganizationAdapter:
    """Тесты OrganizationAdapter."""

    async def test_org_exists_true(self) -> None:
        oid = str(Id.generate())
        provider = _StubOrganizationProvider({oid: _make_org_dto(oid)})
        adapter = OrganizationAdapter(organization_provider=provider)

        result = await adapter.org_exists(oid)
        assert result is True

    async def test_org_exists_false(self) -> None:
        provider = _StubOrganizationProvider({})
        adapter = OrganizationAdapter(organization_provider=provider)

        result = await adapter.org_exists("nonexistent-id")
        assert result is False

    async def test_get_organization_found(self) -> None:
        oid = str(Id.generate())
        dto = _make_org_dto(oid, name="Found Org")
        provider = _StubOrganizationProvider({oid: dto})
        adapter = OrganizationAdapter(organization_provider=provider)

        result = await adapter.get_organization(oid)
        assert result is not None
        assert result["id"] == oid
        assert result["name"] == "Found Org"

    async def test_get_organization_not_found(self) -> None:
        provider = _StubOrganizationProvider({})
        adapter = OrganizationAdapter(organization_provider=provider)

        result = await adapter.get_organization("nonexistent-id")
        assert result is None
