"""Интеграционные тесты GetChildWorkspacesHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.queries.get_child_workspaces import (
    GetChildWorkspacesQuery,
    GetChildWorkspacesHandler,
)
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker


@pytest.mark.integration
class TestGetChildWorkspacesHandler:
    """Тесты GetChildWorkspacesHandler."""

    @pytest.fixture
    def handler(self, ws_repo) -> GetChildWorkspacesHandler:
        return GetChildWorkspacesHandler(
            ws_repo=ws_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
        )

    async def test_get_children_found(self, handler, make_workspace) -> None:
        parent = await make_workspace()
        child = await make_workspace(parent_workspace_id=parent.id, name="Child WS")
        query = GetChildWorkspacesQuery(
            caller_id=str(Id.generate()), parent_workspace_id=str(parent.id),
        )
        result = await handler.handle(query)

        assert result.total >= 1
        assert any(w.name == "Child WS" for w in result.items)

    async def test_get_children_empty(self, handler, make_workspace) -> None:
        parent = await make_workspace()
        query = GetChildWorkspacesQuery(
            caller_id=str(Id.generate()), parent_workspace_id=str(parent.id),
        )
        result = await handler.handle(query)

        assert result.total == 0
