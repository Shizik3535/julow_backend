"""Интеграционные тесты GetRootWorkspacesHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.queries.get_root_workspaces import (
    GetRootWorkspacesQuery,
    GetRootWorkspacesHandler,
)


@pytest.mark.integration
class TestGetRootWorkspacesHandler:
    """Тесты GetRootWorkspacesHandler."""

    @pytest.fixture
    def handler(self, ws_repo, permission_checker_stub) -> GetRootWorkspacesHandler:
        return GetRootWorkspacesHandler(ws_repo=ws_repo, permission_checker=permission_checker_stub)

    async def test_get_root_workspaces_found(self, handler, make_workspace) -> None:
        await make_workspace(name="Root WS")
        query = GetRootWorkspacesQuery(caller_id=str(Id.generate()))
        result = await handler.handle(query)

        assert result.total >= 1

    async def test_children_excluded_from_root(self, handler, make_workspace) -> None:
        parent = await make_workspace(name="Parent Root")
        child = await make_workspace(parent_workspace_id=parent.id, name="Not Root")
        query = GetRootWorkspacesQuery(caller_id=str(Id.generate()))
        result = await handler.handle(query)

        names = [w.name for w in result.items]
        assert "Not Root" not in names
