"""Интеграционные тесты GetWorkspaceMemberHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.queries.get_workspace_member import (
    GetWorkspaceMemberQuery,
    GetWorkspaceMemberHandler,
)
from app.context.workspace.domain.exceptions.workspace_membership_exceptions import WorkspaceMemberNotFoundException


@pytest.mark.integration
class TestGetWorkspaceMemberHandler:
    """Тесты GetWorkspaceMemberHandler."""

    @pytest.fixture
    def handler(self, ws_membership_repo, ws_repo, permission_checker_stub) -> GetWorkspaceMemberHandler:
        return GetWorkspaceMemberHandler(
            membership_repo=ws_membership_repo,
            ws_repo=ws_repo,
            permission_checker=permission_checker_stub,
        )

    async def test_get_member_found(
        self, handler, make_workspace_with_membership
    ) -> None:
        data = await make_workspace_with_membership()
        ws = data["workspace"]
        owner_id = data["owner_id"]
        query = GetWorkspaceMemberQuery(
            caller_id=str(owner_id), workspace_id=str(ws.id), user_id=str(owner_id),
        )
        result = await handler.handle(query)

        assert result.user_id == str(owner_id)
        assert result.is_active is True

    async def test_get_member_not_found(
        self, handler, make_workspace_with_membership
    ) -> None:
        data = await make_workspace_with_membership()
        ws = data["workspace"]
        owner_id = data["owner_id"]
        query = GetWorkspaceMemberQuery(
            caller_id=str(owner_id), workspace_id=str(ws.id), user_id=str(Id.generate()),
        )
        with pytest.raises(WorkspaceMemberNotFoundException):
            await handler.handle(query)
