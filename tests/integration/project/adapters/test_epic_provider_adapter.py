"""Интеграционные тесты EpicProviderAdapter (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.infrastructure.integration.outboard.epic_provider_adapter import (
    EpicProviderAdapter,
)


@pytest.mark.integration
class TestEpicProviderAdapter:
    """Тесты EpicProviderAdapter — outboard adapter."""

    @pytest.fixture
    def adapter(self, epic_repo) -> EpicProviderAdapter:
        return EpicProviderAdapter(repo=epic_repo)

    async def test_epic_exists_true(self, adapter, make_epic) -> None:
        epic = await make_epic()
        result = await adapter.epic_exists(str(epic.id))
        assert result is True

    async def test_epic_exists_false(self, adapter) -> None:
        result = await adapter.epic_exists(str(Id.generate()))
        assert result is False

    async def test_get_epic_found(self, adapter, make_epic) -> None:
        epic = await make_epic(name="Feature Epic")
        result = await adapter.get_epic(str(epic.id))
        assert result is not None
        assert result.name == "Feature Epic"

    async def test_get_epic_not_found(self, adapter) -> None:
        result = await adapter.get_epic(str(Id.generate()))
        assert result is None

    async def test_get_epics_by_project(self, adapter, make_epic) -> None:
        epic = await make_epic()
        result = await adapter.get_epics_by_project(str(epic.project_id))
        assert len(result) >= 1
