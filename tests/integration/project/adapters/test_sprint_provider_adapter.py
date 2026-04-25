"""Интеграционные тесты SprintProviderAdapter (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.infrastructure.integration.outboard.sprint_provider_adapter import (
    SprintProviderAdapter,
)


@pytest.mark.integration
class TestSprintProviderAdapter:
    """Тесты SprintProviderAdapter — outboard adapter."""

    @pytest.fixture
    def adapter(self, sprint_repo) -> SprintProviderAdapter:
        return SprintProviderAdapter(repo=sprint_repo)

    async def test_sprint_exists_true(self, adapter, make_sprint) -> None:
        sprint = await make_sprint()
        result = await adapter.sprint_exists(str(sprint.id))
        assert result is True

    async def test_sprint_exists_false(self, adapter) -> None:
        result = await adapter.sprint_exists(str(Id.generate()))
        assert result is False

    async def test_get_sprint_found(self, adapter, make_sprint) -> None:
        sprint = await make_sprint(name="Sprint 1")
        result = await adapter.get_sprint(str(sprint.id))
        assert result is not None
        assert result.name == "Sprint 1"

    async def test_get_sprint_not_found(self, adapter) -> None:
        result = await adapter.get_sprint(str(Id.generate()))
        assert result is None

    async def test_get_active_sprint_none(self, adapter, make_sprint) -> None:
        sprint = await make_sprint()  # PLANNING status
        result = await adapter.get_active_sprint(str(sprint.project_id))
        assert result is None

    async def test_get_sprints_by_project(self, adapter, make_sprint) -> None:
        sprint = await make_sprint()
        result = await adapter.get_sprints_by_project(str(sprint.project_id))
        assert len(result) >= 1
