"""Интеграционные тесты SearchWorkspacesHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.queries.search_workspaces import (
    SearchWorkspacesQuery,
    SearchWorkspacesHandler,
)


@pytest.mark.integration
class TestSearchWorkspacesHandler:
    """Тесты SearchWorkspacesHandler."""

    @pytest.fixture
    def handler(self, ws_repo, permission_checker_stub) -> SearchWorkspacesHandler:
        return SearchWorkspacesHandler(
            ws_repo=ws_repo,
            permission_checker=permission_checker_stub,
        )

    async def test_search_by_name(self, handler, make_workspace_with_membership) -> None:
        data1 = await make_workspace_with_membership(name="Alpha Search WS")
        data2 = await make_workspace_with_membership(name="Beta Search WS")
        query = SearchWorkspacesQuery(
            caller_id=str(data1["owner_id"]),
            filters={"name": "Alpha"},
        )
        result = await handler.handle(query)

        assert result.total >= 1
        assert any("Alpha" in w.name for w in result.items)

    async def test_search_by_status(self, handler, make_workspace_with_membership) -> None:
        data = await make_workspace_with_membership(name="Active Search WS")
        query = SearchWorkspacesQuery(
            caller_id=str(data["owner_id"]),
            filters={"status": "active"},
        )
        result = await handler.handle(query)

        assert result.total >= 1

    async def test_search_pagination(self, handler, make_workspace_with_membership) -> None:
        owner_id = Id.generate()
        for i in range(5):
            await make_workspace_with_membership(owner_id=owner_id, name=f"Page WS {i}")
        query = SearchWorkspacesQuery(
            caller_id=str(owner_id),
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
