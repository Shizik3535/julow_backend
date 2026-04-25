"""Интеграционные тесты WorkspaceAdapter (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.infrastructure.integration.inboard.workspace_adapter import (
    WorkspaceAdapter,
)


class _StubWorkspace:
    def __init__(self, id: str, name: str, organization_id: str | None = None):
        self.id = id
        self.name = name
        self.organization_id = organization_id


class _StubWorkspaceProvider:
    """Stub WorkspaceProvider для тестов."""

    def __init__(self, exists: bool = True):
        self._exists = exists

    async def workspace_exists(self, workspace_id: str) -> bool:
        return self._exists

    async def get_workspace(self, workspace_id: str):
        if self._exists:
            return _StubWorkspace(id=workspace_id, name="Stub WS")
        return None


@pytest.mark.integration
class TestWorkspaceAdapter:
    """Тесты WorkspaceAdapter — inboard adapter."""

    async def test_workspace_exists_true(self) -> None:
        provider = _StubWorkspaceProvider(exists=True)
        adapter = WorkspaceAdapter(workspace_provider=provider)
        result = await adapter.workspace_exists(str(Id.generate()))
        assert result is True

    async def test_workspace_exists_false(self) -> None:
        provider = _StubWorkspaceProvider(exists=False)
        adapter = WorkspaceAdapter(workspace_provider=provider)
        result = await adapter.workspace_exists(str(Id.generate()))
        assert result is False

    async def test_get_workspace_found(self) -> None:
        provider = _StubWorkspaceProvider(exists=True)
        adapter = WorkspaceAdapter(workspace_provider=provider)
        result = await adapter.get_workspace(str(Id.generate()))
        assert result is not None
        assert "id" in result

    async def test_get_workspace_not_found(self) -> None:
        provider = _StubWorkspaceProvider(exists=False)
        adapter = WorkspaceAdapter(workspace_provider=provider)
        result = await adapter.get_workspace(str(Id.generate()))
        assert result is None
