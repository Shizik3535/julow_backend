"""Интеграционные тесты GetWorkspaceMembersHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.queries.get_workspace_members import (
    GetWorkspaceMembersQuery,
    GetWorkspaceMembersHandler,
)


@pytest.mark.integration
class TestGetWorkspaceMembersHandler:
    """Тесты GetWorkspaceMembersHandler."""

    @pytest.fixture
    def handler(self, ws_membership_repo, ws_repo, permission_checker_stub) -> GetWorkspaceMembersHandler:
        return GetWorkspaceMembersHandler(
            membership_repo=ws_membership_repo,
            ws_repo=ws_repo,
            permission_checker=permission_checker_stub,
        )

    async def test_get_members_found(self, handler, make_workspace_with_membership) -> None:
        data = await make_workspace_with_membership()
        ws = data["workspace"]
        owner_id = data["owner_id"]
        query = GetWorkspaceMembersQuery(
            caller_id=str(owner_id), workspace_id=str(ws.id),
        )
        result = await handler.handle(query)

        assert result.total >= 1
        assert any(m.user_id == str(owner_id) for m in result.items)

    async def test_get_members_empty(self, handler, make_workspace) -> None:
        ws = await make_workspace()
        query = GetWorkspaceMembersQuery(
            caller_id=str(ws.owner_ids[0]), workspace_id=str(ws.id),
        )
        result = await handler.handle(query)

        assert result.total == 0
        assert result.items == []
