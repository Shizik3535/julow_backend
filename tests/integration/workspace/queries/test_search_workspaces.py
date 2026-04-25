"""Интеграционные тесты SearchWorkspacesHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.queries.search_workspaces import (
    SearchWorkspacesQuery,
    SearchWorkspacesHandler,
)
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker


@pytest.mark.integration
class TestSearchWorkspacesHandler:
    """Тесты SearchWorkspacesHandler."""

    @pytest.fixture
    def handler(self, ws_repo) -> SearchWorkspacesHandler:
        return SearchWorkspacesHandler(
            ws_repo=ws_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
        )

    async def test_search_by_name(self, handler, make_workspace) -> None:
        await make_workspace(name="Alpha Search WS")
        await make_workspace(name="Beta Search WS")
        query = SearchWorkspacesQuery(
            caller_id=str(Id.generate()),
            filters={"name": "Alpha"},
        )
        result = await handler.handle(query)

        assert result.total >= 1
        assert any("Alpha" in w.name for w in result.items)

    async def test_search_by_status(self, handler, make_workspace) -> None:
        await make_workspace(name="Active Search WS")
        query = SearchWorkspacesQuery(
            caller_id=str(Id.generate()),
            filters={"status": "active"},
        )
        result = await handler.handle(query)

        assert result.total >= 1

    async def test_search_pagination(self, handler, make_workspace) -> None:
        for i in range(5):
            await make_workspace(name=f"Page WS {i}")
        query = SearchWorkspacesQuery(
            caller_id=str(Id.generate()),
            offset=0,
            limit=2,
        )
        result = await handler.handle(query)

        assert len(result.items) <= 2

    async def test_search_empty(self, handler) -> None:
        query = SearchWorkspacesQuery(
            caller_id=str(Id.generate()),
            filters={"name": "nonexistent-xyz-abc"},
        )
        result = await handler.handle(query)

        assert result.total == 0
