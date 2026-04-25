"""Интеграционные тесты GetWorkspaceSettingsHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.queries.get_workspace_settings import (
    GetWorkspaceSettingsQuery,
    GetWorkspaceSettingsHandler,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker


@pytest.mark.integration
class TestGetWorkspaceSettingsHandler:
    """Тесты GetWorkspaceSettingsHandler."""

    @pytest.fixture
    def handler(self, ws_repo) -> GetWorkspaceSettingsHandler:
        return GetWorkspaceSettingsHandler(
            ws_repo=ws_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
        )

    async def test_get_settings_found(self, handler, make_workspace) -> None:
        ws = await make_workspace()
        query = GetWorkspaceSettingsQuery(
            caller_id=str(ws.owner_ids[0]), workspace_id=str(ws.id),
        )
        result = await handler.handle(query)

        assert result.workspace_id == str(ws.id)
        assert result.security_policy is not None
        assert result.membership_policy is not None
        assert result.limits is not None

    async def test_get_settings_not_found(self, handler) -> None:
        query = GetWorkspaceSettingsQuery(
            caller_id=str(Id.generate()), workspace_id=str(Id.generate()),
        )
        with pytest.raises(WorkspaceNotFoundException):
            await handler.handle(query)
