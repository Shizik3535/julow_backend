"""Интеграционные тесты GetWorkspaceHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.queries.get_workspace import (
    GetWorkspaceQuery,
    GetWorkspaceHandler,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker


@pytest.mark.integration
class TestGetWorkspaceHandler:
    """Тесты GetWorkspaceHandler."""

    @pytest.fixture
    def handler(self, ws_repo) -> GetWorkspaceHandler:
        return GetWorkspaceHandler(ws_repo=ws_repo, permission_checker=_AlwaysAllowPermissionChecker())

    async def test_get_workspace_found(self, handler, make_workspace) -> None:
        ws = await make_workspace(name="Query WS")
        query = GetWorkspaceQuery(caller_id=str(ws.owner_ids[0]), workspace_id=str(ws.id))
        result = await handler.handle(query)

        assert result.id == str(ws.id)
        assert result.name == "Query WS"
        assert result.status == "active"
        assert result.workspace_type == "team"
        assert result.personalization is not None
        assert result.security_policy is not None
        assert result.membership_policy is not None
        assert result.limits is not None

    async def test_get_workspace_not_found(self, handler) -> None:
        query = GetWorkspaceQuery(caller_id=str(Id.generate()), workspace_id=str(Id.generate()))
        with pytest.raises(WorkspaceNotFoundException):
            await handler.handle(query)
