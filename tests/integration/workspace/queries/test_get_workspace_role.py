"""Интеграционные тесты GetWorkspaceRoleHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.queries.get_workspace_role import (
    GetWorkspaceRoleQuery,
    GetWorkspaceRoleHandler,
)
from app.context.workspace.domain.exceptions.workspace_role_exceptions import WorkspaceRoleNotFoundException
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker


@pytest.mark.integration
class TestGetWorkspaceRoleHandler:
    """Тесты GetWorkspaceRoleHandler."""

    @pytest.fixture
    def handler(self, ws_role_repo) -> GetWorkspaceRoleHandler:
        return GetWorkspaceRoleHandler(
            role_repo=ws_role_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
        )

    async def test_get_role_found(self, handler, make_workspace_role) -> None:
        role = await make_workspace_role(name="query-role")
        query = GetWorkspaceRoleQuery(caller_id=str(Id.generate()), role_id=str(role.id))
        result = await handler.handle(query)

        assert result.id == str(role.id)
        assert result.name == "query-role"
        assert result.is_system is False

    async def test_get_system_role_no_permission_check(self, handler, ws_role_repo) -> None:
        from app.context.workspace.domain.aggregates.workspace_role import WorkspaceRole

        role = WorkspaceRole.create_system(name="sys-query", permissions=["ws.*"])
        role.clear_domain_events()
        await ws_role_repo.add(role)

        query = GetWorkspaceRoleQuery(caller_id=str(Id.generate()), role_id=str(role.id))
        result = await handler.handle(query)

        assert result.is_system is True

    async def test_get_role_not_found(self, handler) -> None:
        query = GetWorkspaceRoleQuery(caller_id=str(Id.generate()), role_id=str(Id.generate()))
        with pytest.raises(WorkspaceRoleNotFoundException):
            await handler.handle(query)
