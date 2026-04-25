"""
Интеграционные тесты WorkspaceProviderAdapter (outboard).

Адаптер предоставляет данные workspace другим BC через WorkspaceProvider.
Использует реальные SqlWorkspaceRepository для проверки маппинга AR → DTO.
"""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.infrastructure.integration.outboard.workspace_provider_adapter import WorkspaceProviderAdapter


@pytest.mark.integration
class TestWorkspaceProviderAdapter:
    """Тесты WorkspaceProviderAdapter."""

    async def test_get_workspace_found(self, ws_repo, make_workspace) -> None:
        ws = await make_workspace(name="Provider WS")
        adapter = WorkspaceProviderAdapter(repo=ws_repo)

        result = await adapter.get_workspace(str(ws.id))
        assert result is not None
        assert result.id == str(ws.id)
        assert result.name == "Provider WS"

    async def test_get_workspace_not_found(self, ws_repo) -> None:
        adapter = WorkspaceProviderAdapter(repo=ws_repo)

        result = await adapter.get_workspace(str(Id.generate()))
        assert result is None

    async def test_workspace_exists_true(self, ws_repo, make_workspace) -> None:
        ws = await make_workspace()
        adapter = WorkspaceProviderAdapter(repo=ws_repo)

        result = await adapter.workspace_exists(str(ws.id))
        assert result is True

    async def test_workspace_exists_false(self, ws_repo) -> None:
        adapter = WorkspaceProviderAdapter(repo=ws_repo)

        result = await adapter.workspace_exists(str(Id.generate()))
        assert result is False

    async def test_get_workspaces_by_organization(self, ws_repo, make_workspace) -> None:
        org_id = Id.generate()
        await make_workspace(organization_id=org_id, name="Org WS 1")
        await make_workspace(organization_id=org_id, name="Org WS 2")
        adapter = WorkspaceProviderAdapter(repo=ws_repo)

        result = await adapter.get_workspaces_by_organization(str(org_id))
        assert len(result) == 2
        names = {r.name for r in result}
        assert "Org WS 1" in names
        assert "Org WS 2" in names

    async def test_get_workspaces_by_organization_empty(self, ws_repo) -> None:
        adapter = WorkspaceProviderAdapter(repo=ws_repo)

        result = await adapter.get_workspaces_by_organization(str(Id.generate()))
        assert result == []
