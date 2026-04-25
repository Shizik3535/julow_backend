"""Интеграционные тесты ProjectMembershipProviderAdapter (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.infrastructure.integration.outboard.project_membership_provider_adapter import (
    ProjectMembershipProviderAdapter,
)


@pytest.mark.integration
class TestProjectMembershipProviderAdapter:
    """Тесты ProjectMembershipProviderAdapter — outboard adapter."""

    @pytest.fixture
    def adapter(self, membership_repo) -> ProjectMembershipProviderAdapter:
        return ProjectMembershipProviderAdapter(repo=membership_repo)

    async def test_is_project_member_true(self, adapter, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        result = await adapter.is_project_member(
            project_id=str(data["project"].id),
            user_id=str(data["owner_id"]),
        )
        assert result is True

    async def test_is_project_member_false(self, adapter, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        result = await adapter.is_project_member(
            project_id=str(data["project"].id),
            user_id=str(Id.generate()),
        )
        assert result is False

    async def test_get_member_found(self, adapter, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        result = await adapter.get_member(
            project_id=str(data["project"].id),
            user_id=str(data["owner_id"]),
        )
        assert result is not None
        assert result.user_id == str(data["owner_id"])

    async def test_get_member_not_found(self, adapter, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        result = await adapter.get_member(
            project_id=str(data["project"].id),
            user_id=str(Id.generate()),
        )
        assert result is None

    async def test_get_member_role(self, adapter, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        result = await adapter.get_member_role(
            project_id=str(data["project"].id),
            user_id=str(data["owner_id"]),
        )
        assert result is not None
