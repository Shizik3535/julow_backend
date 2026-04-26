import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_ws_member_with_role
)


@pytest.mark.e2e
class TestRequestWorkspaceDeletion:
    """POST /workspaces/{ws_id}/request-deletion — Запрос удаления (ws.*)."""
    async def test_request_deletion_no_auth(self, client: AsyncClient, workspace_owner):
        """401 — без токена."""
        ws = workspace_owner
        resp = await client.post(f"{API}/workspaces/{ws['ws_id']}/request-deletion")
        assert resp.status_code == 401
    async def test_request_deletion_forbidden_manager(self, client: AsyncClient, workspace_owner):
        """403 — manager."""
        ws = workspace_owner
        manager = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=manager["user_id"],
            role_name="manager"
        )
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/request-deletion",
            headers=auth_headers(manager["access_token"])
        )
        assert resp.status_code == 403
    async def test_request_deletion_forbidden_member(self, client: AsyncClient, workspace_owner):
        """403 — member."""
        ws = workspace_owner
        member = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=member["user_id"],
            role_name="member"
        )
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/request-deletion",
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 403
    async def test_request_deletion_not_found(self, client: AsyncClient):
        """404 — несуществующий workspace."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/workspaces/00000000-0000-0000-0000-000000000000/request-deletion",
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 404
    async def test_request_deletion_conflict_duplicate(self, client: AsyncClient, workspace_owner):
        """409 — повторный запрос удаления."""
        ws = workspace_owner
        await client.post(
            f"{API}/workspaces/{ws['ws_id']}/request-deletion",
            headers=auth_headers(ws["access_token"])
        )
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/request-deletion",
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 409
    async def test_request_deletion_success_owner(self, client: AsyncClient, workspace_owner):
        """200 — owner запрашивает удаление (через ws.*)."""
        ws = workspace_owner
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/request-deletion",
            headers=auth_headers(ws["access_token"])
        )
        assert resp.status_code == 200
    async def test_request_deletion_forbidden_admin(self, client: AsyncClient, workspace_owner):
        """403 — admin (нет ws.*, только ws.settings.*)."""
        ws = workspace_owner
        admin = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=admin["user_id"],
            role_name="admin"
        )
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/request-deletion",
            headers=auth_headers(admin["access_token"])
        )
        assert resp.status_code == 403
