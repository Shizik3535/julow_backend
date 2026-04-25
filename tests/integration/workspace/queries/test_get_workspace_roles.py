"""Интеграционные тесты GetWorkspaceRolesHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.queries.get_workspace_roles import (
    GetWorkspaceRolesQuery,
    GetWorkspaceRolesHandler,
)
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker


@pytest.mark.integration
class TestGetWorkspaceRolesHandler:
    """Тесты GetWorkspaceRolesHandler."""

    @pytest.fixture
    def handler(self, ws_role_repo) -> GetWorkspaceRolesHandler:
        return GetWorkspaceRolesHandler(
            role_repo=ws_role_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
        )

    async def test_get_roles_by_workspace(self, handler, make_workspace_role) -> None:
        role = await make_workspace_role(name="list-role")
        query = GetWorkspaceRolesQuery(
            caller_id=str(Id.generate()), workspace_id=str(role.workspace_id),
        )
        result = await handler.handle(query)

        assert result.total >= 1
        names = [r.name for r in result.items]
        assert "list-role" in names

    async def test_get_system_roles_only(self, handler, ws_role_repo) -> None:
        from app.context.workspace.domain.aggregates.workspace_role import WorkspaceRole

        role = WorkspaceRole.create_system(name="sys-list", permissions=["ws.*"])
        role.clear_domain_events()
        await ws_role_repo.add(role)

        query = GetWorkspaceRolesQuery(
            caller_id=str(Id.generate()), workspace_id=str(Id.generate()), system_only=True,
        )
        result = await handler.handle(query)

        assert all(r.is_system for r in result.items)

    async def test_get_roles_empty(self, handler) -> None:
        query = GetWorkspaceRolesQuery(
            caller_id=str(Id.generate()), workspace_id=str(Id.generate()),
        )
        result = await handler.handle(query)

        # Системные роли (workspace_id IS NULL) всегда включаются
        assert all(r.is_system for r in result.items)
        assert not any(not r.is_system for r in result.items)
