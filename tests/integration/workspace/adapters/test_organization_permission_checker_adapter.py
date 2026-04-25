"""
Интеграционные тесты OrganizationPermissionCheckerAdapter (inboard).

Адаптер делегирует в OrganizationPermissionProvider (outboard Organization BC).
Тестируем через stub provider.
"""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.ports.integration.outboard.organization_permission_provider import (
    OrganizationPermissionProvider,
)
from app.context.workspace.infrastructure.integration.inboard.organization_permission_checker_adapter import (
    OrganizationPermissionCheckerAdapter,
)


class _StubOrgPermissionProvider(OrganizationPermissionProvider):
    """Stub outboard-провайдер Organization Permission."""

    def __init__(self, allowed: set[tuple[str, str, str]] | None = None):
        self._allowed = allowed or set()

    async def has_permission(self, user_id: str, org_id: str, permission: str) -> bool:
        return (user_id, org_id, permission) in self._allowed


@pytest.mark.integration
class TestOrganizationPermissionCheckerAdapter:
    """Тесты OrganizationPermissionCheckerAdapter."""

    async def test_has_permission_true(self) -> None:
        uid = str(Id.generate())
        oid = str(Id.generate())
        provider = _StubOrgPermissionProvider({(uid, oid, "workspaces.create")})
        adapter = OrganizationPermissionCheckerAdapter(org_permission_provider=provider)

        result = await adapter.has_permission(user_id=uid, org_id=oid, permission="workspaces.create")
        assert result is True

    async def test_has_permission_false(self) -> None:
        uid = str(Id.generate())
        oid = str(Id.generate())
        provider = _StubOrgPermissionProvider(set())
        adapter = OrganizationPermissionCheckerAdapter(org_permission_provider=provider)

        result = await adapter.has_permission(user_id=uid, org_id=oid, permission="workspaces.create")
        assert result is False

    async def test_has_permission_wildcard_delegated_to_org(self) -> None:
        uid = str(Id.generate())
        oid = str(Id.generate())
        provider = _StubOrgPermissionProvider({(uid, oid, "workspaces.*")})
        adapter = OrganizationPermissionCheckerAdapter(org_permission_provider=provider)

        result = await adapter.has_permission(user_id=uid, org_id=oid, permission="workspaces.*")
        assert result is True
