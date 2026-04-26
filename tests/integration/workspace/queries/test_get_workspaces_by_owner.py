"""Интеграционные тесты GetWorkspacesByOwnerHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.queries.get_workspaces_by_owner import (
    GetWorkspacesByOwnerQuery,
    GetWorkspacesByOwnerHandler,
)


@pytest.mark.integration
class TestGetWorkspacesByOwnerHandler:
    """Тесты GetWorkspacesByOwnerHandler."""

    @pytest.fixture
    def handler(self, ws_repo, permission_checker_stub) -> GetWorkspacesByOwnerHandler:
        return GetWorkspacesByOwnerHandler(ws_repo=ws_repo, permission_checker=permission_checker_stub)

    async def test_get_by_owner_found(self, handler, make_workspace) -> None:
        owner_id = Id.generate()
        await make_workspace(owner_id=owner_id, name="Owner WS")
        query = GetWorkspacesByOwnerQuery(caller_id=str(owner_id), owner_id=str(owner_id))
        result = await handler.handle(query)

        assert result.total >= 1

    async def test_get_by_owner_empty(self, handler) -> None:
        query = GetWorkspacesByOwnerQuery(caller_id=str(Id.generate()), owner_id=str(Id.generate()))
        result = await handler.handle(query)

        assert result.total == 0
