"""Интеграционные тесты ProjectPermissionProviderImpl (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.infrastructure.integration.outboard.project_permission_provider_impl import (
    ProjectPermissionProviderImpl,
)
from tests.integration.project.conftest import _AlwaysAllowProjectPermissionChecker


@pytest.mark.integration
class TestProjectPermissionProviderImpl:
    """Тесты ProjectPermissionProviderImpl — outboard adapter."""

    @pytest.fixture
    def adapter(self, permission_checker_stub) -> ProjectPermissionProviderImpl:
        return ProjectPermissionProviderImpl(checker=permission_checker_stub)

    async def test_has_permission_true(self, adapter) -> None:
        result = await adapter.has_permission(
            user_id=str(Id.generate()),
            project_id=str(Id.generate()),
            permission="tasks.read",
        )
        assert result is True

    async def test_has_permission_with_deny_checker(self) -> None:
        class _DenyChecker(_AlwaysAllowProjectPermissionChecker):
            async def has_permission(self, user_id, project_id, permission) -> bool:
                return False

        adapter = ProjectPermissionProviderImpl(checker=_DenyChecker())
        result = await adapter.has_permission(
            user_id=str(Id.generate()),
            project_id=str(Id.generate()),
            permission="tasks.read",
        )
        assert result is False
