"""Интеграционные тесты ProjectRoleProviderAdapter (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.infrastructure.integration.outboard.project_role_provider_adapter import (
    ProjectRoleProviderAdapter,
)


@pytest.mark.integration
class TestProjectRoleProviderAdapter:
    """Тесты ProjectRoleProviderAdapter — outboard adapter."""

    @pytest.fixture
    def adapter(self, role_repo) -> ProjectRoleProviderAdapter:
        return ProjectRoleProviderAdapter(repo=role_repo)

    async def test_get_role_found(self, adapter, make_project_role) -> None:
        role = await make_project_role(name="TestRole")
        result = await adapter.get_role(str(role.id))
        assert result is not None
        assert result.name == "TestRole"

    async def test_get_role_not_found(self, adapter) -> None:
        result = await adapter.get_role(str(Id.generate()))
        assert result is None

    async def test_get_roles_by_project(self, adapter, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        result = await adapter.get_roles_by_project(str(data["project"].id))
        assert len(result) >= 1

    async def test_has_permission(self, adapter, make_project_role) -> None:
        role = await make_project_role(permissions=["content.read"])
        result = await adapter.has_permission(str(role.id), "content.read")
        assert result is True

    async def test_has_permission_false(self, adapter, make_project_role) -> None:
        role = await make_project_role(permissions=["content.read"])
        result = await adapter.has_permission(str(role.id), "content.write")
        assert result is False
