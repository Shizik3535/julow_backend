"""Интеграционные тесты ProjectProviderAdapter (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.infrastructure.integration.outboard.project_provider_adapter import (
    ProjectProviderAdapter,
)


@pytest.mark.integration
class TestProjectProviderAdapter:
    """Тесты ProjectProviderAdapter — outboard adapter."""

    @pytest.fixture
    def adapter(self, project_repo) -> ProjectProviderAdapter:
        return ProjectProviderAdapter(repo=project_repo)

    async def test_project_exists_true(self, adapter, make_project) -> None:
        project = await make_project()
        result = await adapter.project_exists(str(project.id))
        assert result is True

    async def test_project_exists_false(self, adapter) -> None:
        result = await adapter.project_exists(str(Id.generate()))
        assert result is False

    async def test_get_project_found(self, adapter, make_project) -> None:
        project = await make_project(name="Provider Project")
        result = await adapter.get_project(str(project.id))
        assert result is not None
        assert result.name == "Provider Project"

    async def test_get_project_not_found(self, adapter) -> None:
        result = await adapter.get_project(str(Id.generate()))
        assert result is None

    async def test_get_projects_by_workspace(self, adapter, make_project) -> None:
        ws_id = Id.generate()
        await make_project(workspace_id=ws_id)
        result = await adapter.get_projects_by_workspace(str(ws_id))
        assert len(result) >= 1
